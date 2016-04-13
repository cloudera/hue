local copy = {}

copy.shallow_copy = function(t)
  local t2 = {}
  for k,v in pairs(t) do
    t2[k] = v
  end
  return t2
end

return copy
