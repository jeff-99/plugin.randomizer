import sys
from resources.lib.randomizer import plugin

randomizer = plugin.Plugin(sys.argv[1])
randomizer.run(sys.argv[0])
