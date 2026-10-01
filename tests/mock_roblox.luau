-- Минимальная подделка окружения Roblox для запуска серверной логики в luau.exe.
-- Здесь только то, чем пользуется src/server/Duel.luau.

local clock = { now = 1000 }
local queue = {}

local task = {}

function task.delay(seconds, fn, ...)
	table.insert(queue, { at = clock.now + seconds, fn = fn, args = table.pack(...) })
end

function task.defer(fn, ...)
	task.delay(0, fn, ...)
end

function task.spawn(fn, ...)
	local co = coroutine.create(fn)
	local ok, message = coroutine.resume(co, ...)
	assert(ok, message)
end

function task.wait(seconds)
	local co = coroutine.running()
	task.delay(seconds, function()
		local ok, message = coroutine.resume(co)
		assert(ok, message)
	end)
	coroutine.yield()
end

-- Продвигает поддельное время и выполняет всё, что должно было сработать.
local function advance(seconds)
	local target = clock.now + seconds
	while true do
		local bestIndex = nil
		for index, item in queue do
			if item.at <= target and (bestIndex == nil or item.at < queue[bestIndex].at) then
				bestIndex = index
			end
		end
		if not bestIndex then
			break
		end
		local item = table.remove(queue, bestIndex)
		clock.now = math.max(clock.now, item.at)
		item.fn(table.unpack(item.args, 1, item.args.n))
	end
	clock.now = target
end

local function newSignal()
	local signal = { handlers = {} }
	function signal:Connect(fn)
		table.insert(self.handlers, fn)
	end
	function signal:Fire(...)
		for _, fn in self.handlers do
			fn(...)
		end
	end
	return signal
end

local CFrame = {}
local cframeMeta = {}
cframeMeta.__mul = function()
	return setmetatable({}, cframeMeta)
end
function CFrame.new()
	return setmetatable({}, cframeMeta)
end

local inbox = {} -- [player] = { сообщения State }
local rivalInbox = {} -- [player] = { сообщения Rival }
local remotes = {}

local Instance = {}
function Instance.new(className)
	local instance = { ClassName = className }
	if className == "RemoteEvent" then
		instance.OnServerEvent = newSignal()
		function instance:FireClient(player, payload)
			local box = if self.Name == "Rival" then rivalInbox else inbox
			box[player] = box[player] or {}
			table.insert(box[player], payload)
		end
		table.insert(remotes, instance)
	end
	return instance
end

local dummy = {}
local Players = { PlayerRemoving = newSignal(), PlayerAdded = newSignal(), list = {} }
function Players:GetPlayers()
	return self.list
end
function Players:GetPlayerFromCharacter(character)
	return character and character.player
end

local Workspace = {}
function Workspace:GetServerTimeNow()
	return clock.now
end

-- Тест может переключать, считается ли запуск запуском в Studio.
local RunService = { studio = true }
function RunService:IsStudio()
	return self.studio
end

local ReplicatedStorage = {}
function ReplicatedStorage:WaitForChild()
	return dummy
end

local game = {}
function game:GetService(name)
	if name == "Players" then
		return Players
	elseif name == "Workspace" then
		return Workspace
	elseif name == "RunService" then
		return RunService
	end
	return ReplicatedStorage
end

local nextUserId = 100
local function newPlayer(name)
	nextUserId += 1
	local player = { Name = name, DisplayName = name, UserId = nextUserId, Parent = Players, CharacterAdded = newSignal() }
	local humanoid = { Health = 100, Sit = false }
	local character = { Parent = Workspace, player = player, humanoid = humanoid }
	function character:FindFirstChildOfClass()
		return self.humanoid
	end
	function character:PivotTo() end
	humanoid.Parent = character
	player.Character = character
	table.insert(Players.list, player)
	return player
end

local function newSeat()
	local seat = { Occupant = nil, CFrame = CFrame.new(), changed = newSignal() }
	function seat:GetPropertyChangedSignal()
		return self.changed
	end
	function seat:Sit(humanoid)
		self.Occupant = humanoid
		humanoid.Sit = true
		self.changed:Fire()
	end
	function seat:FindFirstChild()
		if not self.Occupant then
			return nil
		end
		return {
			Destroy = function()
				self.Occupant = nil
				self.changed:Fire()
			end,
		}
	end
	return seat
end

local function newWorldTable(id)
	local worldTable = {
		id = id,
		seats = { newSeat(), newSeat() },
		prompts = { { Enabled = true, Triggered = newSignal() }, { Enabled = true, Triggered = newSignal() } },
		status = "",
	}
	worldTable.setStatus = function(text)
		worldTable.status = text
	end
	worldTable.setLamp = function(on)
		worldTable.lamp = on
	end
	worldTable.celebrate = function(seatIndex)
		worldTable.celebrated = seatIndex
	end
	return worldTable
end

-- Игрок выходит из игры: сначала событие PlayerRemoving, затем исчезает персонаж.
local function removePlayer(player, seat)
	Players.PlayerRemoving:Fire(player)
	player.Parent = nil
	if seat and seat.Occupant == player.Character.humanoid then
		seat.Occupant = nil
		seat.changed:Fire()
	end
end

local function act(player, action, payload)
	for _, remote in remotes do
		if remote.Name == "Action" then
			remote.OnServerEvent:Fire(player, action, payload)
		end
	end
end

local function last(player)
	local box = inbox[player]
	return box and box[#box]
end

local function lastRival(player)
	local box = rivalInbox[player]
	return box and box[#box]
end

-- Подставной банк: задания задаёт тест.
local mockTasks = {}
local mockBank = {}
function mockBank.getTasks(subjectId)
	return mockTasks[subjectId] or {}
end
function mockBank.count(subjectId)
	return #mockBank.getTasks(subjectId)
end
function mockBank.load() end
