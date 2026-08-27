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

    pm.test("Job submission returns HTTP 201", function () {
        pm.expect(pm.response.code).to.eql(201);
    });

    if (pm.response.code !== 201) {
        pm.execution.setNextRequest(null);
        return;
    }

    let body;
    try {
        body = pm.response.json();
    } catch (error) {
        pm.test("Job submission has a JSON response body", function () {
            throw error;
        });
        pm.execution.setNextRequest(null);
        return;
    }

    const monitorLink = Array.isArray(body.links)
        ? body.links.find(function (link) { return link.rel === "monitor"; })
        : undefined;
    const location = pm.response.headers.get("Location");
    const monitorHref = location || (monitorLink && monitorLink.href);

    pm.test("Job submission includes a monitor URL", function () {
        pm.expect(monitorHref).to.be.a("string").and.not.empty;
    });

    if (!monitorHref) {
        pm.execution.setNextRequest(null);
        return;
    }

    const jobUrl = resolveLink(monitorHref);
    const jobPath = jobUrl.split(/[?#]/)[0].replace(/\/+$/, "");
    const jobIdMatch = jobPath.match(/\/jobs\/([^/]+)$/);
    const jobIdFromUrl = jobIdMatch && decodeURIComponent(jobIdMatch[1]);
    const jobId = body.jobID || body.id || jobIdFromUrl;

    pm.test("Job ID is available", function () {
        pm.expect(jobId).to.not.be.oneOf([undefined, null, ""]);
    });

    if (jobId === undefined || jobId === null || jobId === "") {
        pm.execution.setNextRequest(null);
        return;
    }

    pm.collectionVariables.set("jobUrl", jobUrl);
    pm.collectionVariables.set("jobId", String(jobId));
    pm.collectionVariables.set("pollAttempt", "0");
    pm.collectionVariables.unset("resultsUrl");
})();
