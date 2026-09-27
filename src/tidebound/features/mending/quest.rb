# A fictional game inside the game. Its state never touches real Pokemon.
module Tidebound::Mending
  START = [9, 10].freeze
  NESTS = [[3, 2], [15, 2], [9, 4]].freeze
  EXIT = [9, 0].freeze
  CELLS = {}
  [
    [[9, 0], [9, 10]],
    [[3, 8], [15, 8]],
    [[3, 4], [15, 4]],
    [[3, 2], [3, 8]],
    [[15, 2], [15, 8]]
  ].each do |a, b|
    x, y = a
    dx = b[0] <=> x
    dy = b[1] <=> y
    loop do
      CELLS[[x, y]] = true
      break if [x, y] == b
      x += dx
      y += dy
    end
  end
  CELLS.freeze
  class Game
    attr_reader :cell, :freed, :bumps
    def initialize
      @cell = START.dup
      @freed = []
      @bumps = 0
    end
    def move(dx, dy)
      p = [@cell[0] + dx, @cell[1] + dy]
      return false unless CELLS[p] && (p != EXIT || @freed.length == 3)
      @cell = p
      true
    end
    def loosen
      i =
        NESTS.each_index.find do |n|
          !@freed.include?(n) && (NESTS[n][0] - @cell[0]).abs + (NESTS[n][1] - @cell[1]).abs <= 1
        end
      @freed << i if i
      i
    end
    def bump
      @cell = START.dup
      @bumps += 1
    end
    def won?
      @cell == EXIT && @freed.length == 3
    end
  end
end
