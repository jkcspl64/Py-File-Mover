#!/usr/bin/env python3

import os
import shutil
import pathlib


def normalize_fp(fp: pathlib.Path):
  if fp.is_absolute():
    return fp
  elif fp.is_symlink():
    return pathlib.Path( os.path.abspath(str(fp)) )
  else:
    return fp.resolve()


class FileOperation:
  def __init__(self):
    self.src = None
    self.dst = None
    self.ready = False
    self.done = False
    self.is_successful = False
    self.overwritten = False
    self.detail = ""
  
  def add_file(self, file, dst_dir, dst_has_file=False):
    self.src = normalize_fp( pathlib.Path(file) )
    if dst_has_file:
      self.dst = normalize_fp( pathlib.Path(dst_dir) )
    else:
      self.dst = normalize_fp( pathlib.Path(pathlib.Path(dst_dir) / self.src.name) )
    self.ready = True
  
  def __as_string(self, oper_type):
    file_name = "None" if not self.src else str(self.src)
    str_template = f"{oper_type}|{file_name}|" + "{}"
    
    if not self.ready:
      return str_template.format("NOT READY")
    elif not self.done:
      return str_template.format("READY")
    else:
      status = "OK" if self.is_successful else "ERROR"
      oper_info = f"{status}|{self.detail}"
      return str_template.format(oper_info)
  
  def __str__(self):
    return self.__as_string("Generic")


class MovableFile(FileOperation):
  def __init__(self):
    super().__init__()
  
  def __str__(self):
    return self._FileOperation__as_string("Move")
  
  @staticmethod
  def from_base(obj: FileOperation):
    resp = MovableFile()
    resp.src = obj.src
    resp.dst = obj.dst
    resp.ready = obj.ready
    resp.done = obj.done
    resp.is_successful = obj.is_successful
    resp.overwritten = obj.overwritten
    resp.detail = obj.detail
    return resp
  
  def run(self, overwrite=False):
    if not self.ready:
      self.detail = "File not added to object"
      return
    
    try:
      if not self.src.exists():
        raise IOError("File doesn't exist in source directory")
      
      if not self.dst.parent.exists() or not self.dst.parent.is_dir():
        raise IOError("Destination dir. doesn't exist or is not a directory")
      
      if not overwrite and self.dst.exists():
        raise IOError("File exists in destination directory")
      elif self.dst.exists():
        self.overwritten = True
      
      shutil.move(self.src, self.dst)
      self.is_successful = True
      self.detail = "OK"
    except (IOError, OSError) as e:
      self.detail = str(e)
      self.overwritten = False
    finally:
      self.done = True


class CopyableFile(FileOperation):
  def __init__(self):
    super().__init__()
  
  def __str__(self):
    return self._FileOperation__as_string("Copy")
  
  @staticmethod
  def from_base(obj: FileOperation):
    resp = CopyableFile()
    resp.src = obj.src
    resp.dst = obj.dst
    resp.ready = obj.ready
    resp.done = obj.done
    resp.is_successful = obj.is_successful
    resp.overwritten = obj.overwritten
    resp.detail = obj.detail
    return resp
  
  def run(self, overwrite=False):
    if not self.ready:
      self.detail = "File not added to object"
      return
    
    try:
      if not self.src.exists():
        raise IOError("File doesn't exist in source directory")
      
      if not self.dst.parent.exists() or not self.dst.parent.is_dir():
        raise IOError("Destination dir. doesn't exist or is not a directory")
      
      if not overwrite and self.dst.exists():
        raise IOError("File exists in destination directory")
      elif self.dst.exists():
        self.overwritten = True
      
      shutil.copy2(self.src, self.dst)
      self.is_successful = True
      self.detail = "OK"
    except (IOError, OSError) as e:
      self.detail = str(e)
      self.overwritten = False
    finally:
      self.done = True
