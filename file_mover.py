#!/usr/bin/env python3

import sys
import pathlib
import argparse

from typing import List
from queue import SimpleQueue
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
  folder_mode.add_argument("-R", "--recursive", help="Process files recursively", action="store_true")
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
  files = [e for e in in_ffp.glob(wcd) if e.is_file()]
  
  for file in files:
    fobj = FileOperation()
    fobj.add_file(file, out_ffp)
    result.append(fobj)
  
  return result


def get_all_files_recursively(root_folder: str, out_folder: str, wildcard):
  root_ffp = normalize_fp( pathlib.Path(root_folder) )
  out_ffp = normalize_fp( pathlib.Path(out_folder) )
  
  if not root_ffp.exists() or not root_ffp.is_dir():
    print("The input (root) folder doesn't exist or is not a folder!", file=sys.stderr)
    exit(-1)
  
  files: List[FileOperation] = []
  in_folders : List[pathlib.Path] = []
  out_folders: List[pathlib.Path] = []
  
  wcd = "*" if wildcard == "ALL" else wildcard
  
  q = SimpleQueue()
  q.put( normalize_fp(pathlib.Path(root_folder)) )
  
  while not q.empty():
    ffp = q.get()
    
    for file in [e for e in ffp.glob(wcd) if e.is_file()]:
      fobj = FileOperation()
      fobj.add_file( file, pathlib.Path(out_ffp / file.relative_to(root_ffp)), dst_has_file=True )
      files.append(fobj)
    
    for folder in [normalize_fp(e) for e in ffp.glob("*") if e.is_dir()]:
      q.put(folder)
      in_folders.append( normalize_fp(folder) )
      out_folders.append(
        normalize_fp( pathlib.Path(out_ffp / folder.relative_to(root_ffp)) )
      )
  
  return (in_folders, out_folders, files)


def main():
  args = parse_args()
  
  in_folders: List[pathlib.Path] = None
  out_folders: List[pathlib.Path] = None
  files: List[FileOperation] = []
  
  if args.input_mode.lower() == "files":
    # File list input mode
    files = get_files_from_txt(args.file_list)
  elif args.input_mode.lower() == "folder":
    # Folder input mode
    if args.recursive:
      in_folders, out_folders, files = get_all_files_recursively(
        args.in_folder, args.out_folder, args.wildcard
      )
    else:
      files = get_files_from_folder(args.in_folder, args.out_folder, args.wildcard)
    
  if args.create_out_dir:
    unique_dst = set([normalize_fp(f.dst.parent) for f in files])
    for dst in unique_dst:
      dst.mkdir(parents=True, exist_ok=True)
  
  if args.recursive and out_folders:
    for folder in out_folders:
      folder.mkdir(parents=True, exist_ok=True)
  
  for file in files:
    fop = None
    if args.oper_type.lower() == "move":
      fop = MovableFile.from_base(file)
    elif args.oper_type.lower() == "copy":
      fop = CopyableFile.from_base(file)
    
    fop.run(args.overwrite)
    print(fop)
  
  if args.oper_type.lower() == "move" and in_folders:
    while len(in_folders) != 0:
      folder = in_folders.pop()
      folder.rmdir()


if __name__ == "__main__":
  main()
