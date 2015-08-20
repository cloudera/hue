-- The MIT License (MIT)
-- 
-- Copyright (c) 2014 Cyril David <cyx@cyx.is>
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

local uri = require("lib/uri-f570bf7")

local insert = table.insert
local concat = table.concat

local format = string.format
local gmatch = string.gmatch
local sub    = string.sub
local gsub   = string.gsub
local find   = string.find

-- identity function
local function identity(val)
	return val
end

-- trim and remove double quotes
local function clean(str)
	  local s = gsub(str, "^%s*(.-)%s*$", "%1")
	  
	  if sub(s, 1, 1) == '"' then
		  s = sub(s, 2, -2)
	  end

	  return s
end

-- given a unix timestamp, return a utc string
local function to_utc_string(time)
	return os.date("%a, %d %b %Y %H:%I:%S GMT", time)
end

local CODEX = {
	{"max_age", "Max-Age=%d", identity},
	{"domain", "Domain=%s", identity},
	{"path", "Path=%s", identity},
	{"expires", "Expires=%s", to_utc_string},
	{"http_only", "HttpOnly", identity},
	{"secure", "Secure", identity},
}

local function build(dict, options)
	options = options or {}

	local res = {}

	for k, v in pairs(dict) do
		insert(res, format("%s=%s", k, uri.encode(v)))
	end

	for _, tuple in ipairs(CODEX) do
		local key, template, fn = unpack(tuple)
		local val = options[key]

		if val then
			insert(res, format(template, fn(val)))
		end
	end

	return concat(res, "; ")
end

local function parse(data)
	local res = {}

	for pair in gmatch(data, "[^;]+") do
		local eq = find(pair, "=")

		if eq then
			local key = clean(sub(pair, 1, eq-1))
			local val = clean(sub(pair, eq+1))

			if not res[key] then
				res[key] = uri.decode(val)
			end
		end
	end

	return res
end

return {
	build = build,
	parse = parse
}
