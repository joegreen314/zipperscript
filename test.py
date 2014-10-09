"""from optparse import OptionParser
parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")
parser.add_option("-s", "--sooo", action="store_true", dest="var", default = False, help = "testing you are")

(options, args) = parser.parse_args()"""


from optparse import OptionParser


parser = OptionParser()

parser.add_option("-s", action="store_false", dest="showUI", default = True, help = "suppress UI messages")

(options, args) = parser.parse_args()

print options.showUI