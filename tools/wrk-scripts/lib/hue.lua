local argparse = require("lib/argparse")
local cookie = require("lib/cookie")
local uri = require("lib/uri-f570bf7")
local inspect = require("lib/inspect")

local hue = {}

hue.parse_args = function(args)
	local parser = argparse()
	parser:option "-X" "--method"
		:description "HTTP method"
	parser:option "-s" "--session"
		:description "session cookie"

	parser:flag "-v" "--verbose"
		:description "print verbosely"

	local args = parser:parse(args)

	if args["method"] then
		wrk.method = args["method"]
	end

	if args["session"] then
		wrk.headers["Cookie"] = cookie.build({
			sessionid=args["session"]
		})
	end

	hue.verbose = args.verbose
end

hue.handle_redirect = function(status, location)
	local location = uri.parse(location)

	wrk.scheme = location.scheme
	wrk.host = location.host
	wrk.port = location.port
	wrk.path = location.path

	if location.query then
		wrk.path = wrk.path .. "?" .. location.query
	end

	if location.fragment then
		wrk.path = wrk.path .. "#" .. location.fragment
	end

	if status == 303 then
		wrk.method = "GET"
	end
end

hue.set_cookies = function(set_cookie)
	local req_cookie = cookie.parse(wrk.headers["Cookie"] or "")
	local rep_cookie = cookie.parse(set_cookie)

	for key, val in pairs(rep_cookie) do
		-- ignore the cookie metadata
		if key ~= "Path" and key ~= "expires" and key ~= "HttpOnly" and key ~= "Max-Age" then
			req_cookie[key] = val
		end

		-- Make sure we handle the 
		if key == "csrftoken" then
			wrk.headers["X-CSRFToken"] = val
		end
	end

	wrk.headers["Cookie"] = cookie.build(req_cookie)
end

return hue
