-- Точка входа сервера: загружает банк заданий, строит класс и запускает матчи за партами.
local Config = require(script.Parent.Config)
local World = require(script.Parent.World)
local Bank = require(script.Parent.Bank)
local Duel = require(script.Parent.Duel)

Bank.load()
local world = World.build(Config.tableCount, { randomTask = Bank.randomTextTask })
Duel.start(world.tables, world.setScoreboard)
