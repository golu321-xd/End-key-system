-- rayfield_script.lua (paste into your exploit's script)
local HttpService = game:GetService("HttpService")
local function getHWID()
    local ok, id = pcall(function() return tostring(game:GetService("RbxAnalyticsService"):GetClientId()) end)
    if ok and id then return id end
    if syn and syn.get_hwid then return syn.get_hwid() end
    return "HWID_NOT_FOUND"
end

local function http_get(url)
    if syn and syn.request then
        local r = syn.request({Url=url, Method="GET"})
        return r.Body, r.StatusCode
    elseif http_request then
        local r = http_request({Url=url, Method="GET"})
        return r.Body, r.StatusCode
    end
    return nil, 0
end

local function validate_key(key)
    local hwid = getHWID()
    if hwid == "HWID_NOT_FOUND" then return false, "hwid_missing" end
    local api = "https://REPLACE_WITH_API_URL/validate?key="..key.."&hwid="..hwid
    local body, status = http_get(api)
    if not body then return false, "http_fail" end
    local ok, data = pcall(function() return HttpService:JSONDecode(body) end)
    if not ok then return false, "json_error" end
    if data.valid then return true, data.expires_at else return false, data.reason end
end

-- Example usage: paste key below before running
local user_key = "" -- put key here
local ok, info = validate_key(user_key)
if ok then
    print("Verified, continue running script.")
else
    game.Players.LocalPlayer:Kick("get key from discord server")
end
