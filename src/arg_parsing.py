import argparse
import os
from globals import VERSION, APP_NAME


parser = argparse.ArgumentParser(description="Convert note formats", prog='{}.py'.format(APP_NAME))

parser.add_argument('-v', '--version', action='version', version='%(prog)s Version {}'.format(VERSION))
parser.add_argument("-s", "--silent", action="store_true", help="No output to console")
group = parser.add_mutually_exclusive_group()
group.add_argument("-g", "--gui", action="store_false", help="No gui interface")
group.add_argument('-q', "--quickset", choices=['q_own_notes', 'gfm', 'obsidian', 'pdf'],
                    help="Choose a quick conversion setting rather than the one in the config.ini file")
parser.add_argument('source', nargs='?', default=os.getcwd(),
                    help='sub folder of current folder containing one or more *.nsx files, or the name of a '
                         'single nsx file.  For example "my_nsx_files" or "my_nsx_files/my_nsx_file.nsx".  '
                         'If not included will search and use current folder')
subparsers = parser.add_subparsers(title='manual',
                                   description='Options and arguments for manual setting of conversion',
                                   help='For help on manual settings use "manual -h"')

parser_manual = subparsers.add_parser('manual', help='configure conversion using command line options')
meta_group = parser_manual.add_argument_group(title='Meta Data options')
meta_group.add_argument('-m', '--meta', action="store_true",
                        help='Include meta data in output file. If not used the rest of the meta data options '
                             'will NOT be used even if provided')
meta_group.add_argument('-y', '--yaml', action="store_true", help='Place meta data in a YAML header')
meta_group.add_argument('-n', '--notetitle', action="store_true", help='Include note title in meta data')
meta_group.add_argument('-c', '--creation', action="store_true", help='Include note creation time in meta data')
meta_group.add_argument('-z', '--modtime', action="store_true", help='Include note modified time in meta data')
meta_group.add_argument('-t', '--tags', action="store_true", help='Include note modified time in meta data')
meta_group.add_argument('--spaces', action="store_true", help='Allow spaces in tag name')
meta_group.add_argument('--split', action="store_true", help='Split tags')
parser_manual.add_argument('--ctef', action="store_true", help='Add meta creation time to end of note filename')
parser_manual.add_argument('-i', "--images", choices=['markdown-strict', 'gfm', 'obsidian'],
                           help="Choose image format for image links")
parser_manual.add_argument('-x', '--exportformat', choices=['q_own_notes', 'gfm', 'obsidian', 'pdf'],
                           help="q_own_notes=markdown-strict minus html plus pipetables, "
                                "gfm=git-flavoured markdown, "
                                "obsidian=git-flavoured markdown, "
                                "pdf=pdf")
parser_manual.add_argument('export_folder_name', nargs='?', default='notes',
                           help='If not provided defaults to "notes".  This is the name of sub folder to place '
                                'exported notebooks into.  If a source folder has been provided the notes folder '
                                'wil be created in that folder. If no source is provided the notes folder will '
                                'be created in the current folder.')
parser_manual.add_argument('attachment_folder_name', nargs='?', default='attachments',
                           help='Name of sub folder to create, inside of the notebook folders to store images '
                                'and attachments.  Default=attachments')




args = parser.parse_args()
print(args.gui)
# answer = args.x ** args.y
#
# if args.quiet:
#     print(answer)
# elif args.verbose:
#     print("{} to the power {} equals {}".format(args.x, args.y, answer))
# else:
#     print("{}^{} == {}".format(args.x, args.y, answer))

# if __name__ == '__main__':
