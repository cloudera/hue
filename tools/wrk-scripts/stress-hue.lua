-- This test repeatably GETs the same url.

local hue = require("lib/hue")
local inspect = require("lib/inspect")

function init(args)
	hue.parse_args(args)
end

function request()
	request_data = {
		method = wrk.method,
		path = wrk.path,
		headers = wrk.headers,
		body = wrk.body,
	}

	return wrk.format()
end

function response(status, headers, body)
	data = {
		request = request_data,
		response = {
			status = status,
			headers = headers,
		}
	}

	if headers["Set-Cookie"] then
		hue.set_cookies(headers["Set-Cookie"])
	end

	if status == 301 or status == 302 or status == 303 or status == 307 or status == 308 then
		hue.handle_redirect(status, headers["Location"])
	elseif status >= 399 then
		-- log the error
		data.response.body = body
	end

	if hue.verbose then
		print(
			inspect.inspect(data)
			..
			"\n------------------------------------------------------")
	end
end
