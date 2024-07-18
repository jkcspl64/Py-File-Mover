#!/usr/bin/env python3

import sys
import pathlib
import argparse

from typing import List
from move_objs import normalize_fp, FileOperation, MovableFile, CopyableFile


def parse_args():
  parser = argparse.ArgumentParser()
  parser.add_argument(
    "-V", "--overwrite", help="Allow overwritting existing files",
    action="store_true"
  )
  parser.add_argument(
    "-C", "--create-out-dir",
    help="Create output directory and subdirectories if they don't exist",
    action="store_true"
  )
  parser.add_argument("oper_type", help="The operation to do on the files (move or copy; mandatory)", choices=["move", "copy"])
  
  input_mode = parser.add_subparsers(
    title="Input mode", description="The following are valid input modes:",
    dest="input_mode"
  )
  
  file_mode = input_mode.add_parser("files", help="Move/copy a list of files")
  file_mode.add_argument("file_list", help="The list of files to be processed (mandatory)")
  
  folder_mode = input_mode.add_parser("folder", help="Move/copy files from a specified folder")
  folder_mode.add_argument("in_folder", help="The folder where the to-be processed files are (mandatory)")
  folder_mode.add_argument("out_folder", help="The folder where the processed files will be (mandatory)")
  folder_mode.add_argument(
    "-w", "--wildcard",
    help="A wildcard specifying which files to process (default: ALL)",
    default="ALL"
  )
  
  return parser.parse_args()


def get_files_from_txt(txt_file):
  fp = pathlib.Path(txt_file)
  
  if not fp.exists() or not fp.is_file():
    print("The input file doesn't exist or is not a file!", file=sys.stderr)
    exit(-1)
  
  result: List[FileOperation] = []
  
  with open(str(fp), "r", encoding="utf-8") as fhand:
    for line in fhand:
      line_pieces = [e.strip() for e in line.strip().split("|")]
      fobj = FileOperation()
      fobj.add_file(line_pieces[0].strip(), line_pieces[1].strip())
      result.append(fobj)
  
  return result


def get_files_from_folder(in_folder: str, out_folder: str, wildcard):
  in_ffp = normalize_fp( pathlib.Path(in_folder) )
  out_ffp = normalize_fp( pathlib.Path(out_folder) )
  
  if not in_ffp.exists() or not in_ffp.is_dir():
    print("The input folder doesn't exist or is not a folder!", file=sys.stderr)
    exit(-1)
    
  result: List[FileOperation] = []
  wcd = "*" if wildcard == "ALL" else wildcard
  files = in_ffp.glob(wcd)
  
  for file in files:
    fobj = FileOperation()
    fobj.add_file(file, out_ffp)
    result.append(fobj)
  
  return result
  

def main():
  args = parse_args()
  
  files: List[FileOperation] = []
  
  if args.input_mode.lower() == "files":
    # File list input mode
    files = get_files_from_txt(args.file_list)
  elif args.input_mode.lower() == "folder":
    # Folder input mode
    files = get_files_from_folder(args.in_folder, args.out_folder, args.wildcard)
    
  if args.create_out_dir:
    unique_dst = set([normalize_fp(f.dst.parent) for f in files])
    for dst in unique_dst:
      dst.mkdir(parents=True, exist_ok=True)
  
  for file in files:
    fop = None
    if args.oper_type.lower() == "move":
      fop = MovableFile.from_base(file)
    elif args.oper_type.lower() == "copy":
      fop = CopyableFile.from_base(file)
    
    fop.run(args.overwrite)
    print(fop)


if __name__ == "__main__":
  main()
