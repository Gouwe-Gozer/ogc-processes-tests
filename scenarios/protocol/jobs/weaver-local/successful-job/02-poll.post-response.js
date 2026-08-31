(function () {
    function resolveLink(href) {
        const value = pm.variables.replaceIn(String(href || "").trim());
        if (/^https?:\/\//i.test(value)) {
            return value;
        }

        const requestUrl = pm.variables.replaceIn(pm.request.url.toString());
        const origin = requestUrl.match(/^(https?:\/\/[^/]+)/i);
        if (value.startsWith("/") && origin) {
            return origin[1] + value;
        }

        const requestPath = requestUrl.split(/[?#]/)[0];
        const lastSlash = requestPath.lastIndexOf("/");
        if (lastSlash >= 0) {
            return requestPath.slice(0, lastSlash + 1) + value.replace(/^\.\//, "");
        }
        return value;
    }

    pm.test("Job status request returns HTTP 200", function () {
        pm.expect(pm.response.code).to.eql(200);
    });

    if (pm.response.code !== 200) {
        pm.execution.setNextRequest(null);
        return;
    }

    let body;
    try {
        body = pm.response.json();
    } catch (error) {
        pm.test("Job status has a JSON response body", function () {
            throw error;
        });
        pm.execution.setNextRequest(null);
        return;
    }

    const status = typeof body.status === "string" ? body.status.toLowerCase() : "";
    pm.collectionVariables.set("jobStatus", status);

    if (status === "accepted" || status === "running") {
        const attempt = Number(pm.collectionVariables.get("pollAttempt") || 0) + 1;
        const maximum = Number(pm.collectionVariables.get("maxPollAttempts") || 60);
        pm.collectionVariables.set("pollAttempt", String(attempt));

        pm.test("Job polling stays within the configured limit", function () {
            pm.expect(attempt).to.be.below(maximum);
        });

        if (attempt >= maximum) {
            pm.execution.setNextRequest(null);
            return;
        }

        const delay = Math.max(0, Number(pm.collectionVariables.get("pollDelayMs") || 1000));
        setTimeout(function () {
            pm.execution.setNextRequest(pm.info.requestId);
        }, delay);
        return;
    }

    if (status === "successful") {
        const resultsRelation = "http://www.opengis.net/def/rel/ogc/1.0/results";
        const resultsLink = Array.isArray(body.links)
            ? body.links.find(function (link) {
                return link.rel === resultsRelation || link.rel === "results";
            })
            : undefined;
        const resultsHref = resultsLink && resultsLink.href;

        pm.test("Successful job includes a results URL", function () {
            pm.expect(resultsHref).to.be.a("string").and.not.empty;
        });

        if (!resultsHref) {
            pm.execution.setNextRequest(null);
            return;
        }

        pm.collectionVariables.set("resultsUrl", resolveLink(resultsHref));
        pm.collectionVariables.unset("pollAttempt");
        return;
    }

    pm.test("Job reaches the successful state", function () {
        pm.expect(status, body.message || "Unexpected job status").to.eql("successful");
    });
    pm.execution.setNextRequest(null);
})();
