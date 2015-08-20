-- The MIT License (MIT)
-- 
-- Copyright (c) 2014 Cyril David <cyx@cyx.is>
-- Copyright (c) 2011-2013 Bertrand Mansion <bmansion@mamasam.com>
-- 
-- Permission is hereby granted, free of charge, to any person obtaining a copy
-- of this software and associated documentation files (the "Software"), to deal
-- in the Software without restriction, including without limitation the rights
-- to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
-- copies of the Software, and to permit persons to whom the Software is
-- furnished to do so, subject to the following conditions:
-- 
-- The above copyright notice and this permission notice shall be included in
-- all copies or substantial portions of the Software.
-- 
-- THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
-- IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
-- FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
-- AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
-- LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
-- OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
-- THE SOFTWARE.

-- == list of known and common scheme ports
--
-- @see http://www.iana.org/assignments/uri-schemes.html
--
local SERVICES = {
	acap     = 674,
	cap      = 1026,
	dict     = 2628,
	ftp      = 21,
	gopher   = 70,
	http     = 80,
	https    = 443,
	iax      = 4569,
	icap     = 1344,
	imap     = 143,
	ipp      = 631,
	ldap     = 389,
	mtqp     = 1038,
	mupdate  = 3905,
	news     = 2009,
	nfs      = 2049,
	nntp     = 119,
	rtsp     = 554,
	sip      = 5060,
	snmp     = 161,
	telnet   = 23,
	tftp     = 69,
	vemmi    = 575,
	afs      = 1483,
	jms      = 5673,
	rsync    = 873,
	prospero = 191,
	videotex = 516
}

local LEGAL = {
	["-"] = true, ["_"] = true, ["."] = true, ["!"] = true,
	["~"] = true, ["*"] = true, ["'"] = true, ["("] = true,
	[")"] = true, [":"] = true, ["@"] = true, ["&"] = true,
	["="] = true, ["+"] = true, ["$"] = true, [","] = true,
	[";"] = true -- can be used for parameters in path
}

-- aggressive caching of methods
local gsub   = string.gsub
local char   = string.char
local byte   = string.byte
local upper  = string.upper
local lower  = string.lower
local format = string.format

-- forward declaration of helper utilities
local util = {}

local function decode(str)
	local str = gsub(str, "+", " ")

	return (gsub(str, "%%(%x%x)", function(c)
			return char(tonumber(c, 16))
	end))
end

local function encode(str)
	return (gsub(str, "([^A-Za-z0-9%_%.%-%~])", function(v)
			return upper(format("%%%02x", byte(v)))
	end))
end

-- Build a URL given a table with the fields:
--
--	- scheme
--	- user
--	- password
--	- host
--	- port
--	- path
--	- query
--	- fragment
--
-- Example:
--
--	local url = uri.build({
--		scheme = "http",
--		host = "example.com",
--		path = "/some/path"
--	})
--
--	assert(url == "http://example.com/some/path")
--
local function build(uri)
	local url = ""

	if uri.path then
		local path = uri.path
		
		gsub(path, "([^/]+)", function (s) return util.encode_segment(s) end)

		url = url .. tostring(path)
	end

	if uri.query then
		local qstring = tostring(uri.query)
		if qstring ~= "" then
			url = url .. "?" .. qstring
		end
	end

	if uri.host then
		local authority = uri.host

		if uri.port and uri.scheme and SERVICES[uri.scheme] ~= uri.port then
			authority = authority .. ":" .. uri.port
		end

		local userinfo

		if uri.user and uri.user ~= "" then
			userinfo = encode(uri.user)

			if uri.password then
				userinfo = userinfo .. ":" .. encode(uri.password)
			end
		end

		if userinfo and userinfo ~= "" then
			authority = userinfo .. "@" .. authority
		end

		if authority then
			if url ~= "" then
				url = "//" .. authority .. "/" .. gsub(url, "^/+", "")
			else
				url = "//" .. authority
			end
		end
	end

	if uri.scheme then
		url = uri.scheme .. ":" .. url
	end

	if uri.fragment then
		url = url .. "#" .. uri.fragment
	end

	return url
end

-- Parse the url into the designated parts.
--
-- Depending on the url, the following parts will be available:
--
--	- scheme
--	- userinfo
--	- user
--	- password
--	- authority
--	- host
--	- port
--	- path
--      - query
--      - fragment
--
-- Usage:
--
--     local u = uri.parse("http://john:monkey@example.com/some/path#h1")
--
--     assert(u.host == "example.com")
--     assert(u.scheme == "http")
--     assert(u.user == "john")
--     assert(u.password == "monkey")
--     assert(u.path == "/some/path")
--     assert(u.fragment == "h1")
--
local function parse(url)
	local uri = { query = nil }

	util.set_authority(uri, "")

	local url = tostring(url or "")

	url = gsub(url, "#(.*)$", function(v)
		uri.fragment = v
		return ""
	end)

	url = gsub(url, "^([%w][%w%+%-%.]*)%:", function(v)
		uri.scheme = lower(v)
		return ""
	end)

	url = gsub(url, "%?(.*)", function(v)
		uri.query = v
		return ""
	end)

	url = gsub(url, "^//([^/]*)", function(v)
		util.set_authority(uri, v)
		return ""
	end)

	uri.path = decode(url)

	return uri
end

function util.encode_segment(s)
	local function encode_legal(c)
		if LEGAL[c] then
			return c
		end

		return encode(c)
	end

	return gsub(s, "([^a-zA-Z0-9])", encode_legal)
end

-- set the authority part of the url
--
-- The authority is parsed to find the user, password, port and host if available.
-- @param authority The string representing the authority
-- @return a string with what remains after the authority was parsed
function util.set_authority(uri, authority)
	uri.authority = authority
	uri.port = nil
	uri.host = nil
	uri.userinfo = nil
	uri.user = nil
	uri.password = nil

	authority = gsub(authority, "^([^@]*)@", function(v)
		uri.userinfo = decode(v)
		return ""
	end)

	authority = gsub(authority, "^%[[^%]]+%]", function(v)
		-- ipv6
		uri.host = v
		return ""
	end)

	authority = gsub(authority, ":([^:]*)$", function(v)
		uri.port = tonumber(v)
		return ""
	end)

	if authority ~= "" and not uri.host then
		uri.host = lower(authority)
	end

	if uri.userinfo then
		local userinfo = uri.userinfo

		userinfo = gsub(userinfo, ":([^:]*)$", function(v)
				uri.password = v
				return ""
		end)

		uri.user = userinfo
	end

	return authority
end

local uri = {
	build = build,
	parse = parse,
	encode = encode,
	decode = decode
}

return uri
