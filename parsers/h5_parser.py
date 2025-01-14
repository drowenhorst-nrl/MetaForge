from parsers.metaforgeparser import MetaForgeParser
from typing import List
from pathlib import Path
from uuid import UUID

import os
import h5py
import numpy

from parsers.metaforgeparser import MetaForgeParser

class H5Parser(MetaForgeParser):
  def __init__(self) -> None:
    self.ext_list: list = ('.h5', '.oh5', '.emd')
    self.count: int = 0
    self.file_dict: object = {}

  def human_label(self) -> str:
    return "HDF5 Parser"

  def version(self) -> str:
    return '1.0'

  def uuid(self) -> UUID:
    return UUID('{7420a76b-f0de-4fb1-a932-b6cb969f7af6}')

  def supported_file_extensions(self) -> list:
    return self.ext_list
  
  def accepts_extension(self, extension: str) -> bool:
    return extension in self.ext_list

  def type_dispatch(self, value: any) -> str:
    """
    Perform type dispatch and figure out whether to make an entry
    """
    if isinstance(value, bytes):
      return value.decode('utf-8')
    elif isinstance(value, numpy.void):
      # These are some weirdly encoded numpy arrays!
      return None
    elif isinstance(value, (numpy.ndarray, numpy.generic)):
      if value.shape == (1,):
        return str(value[0])
      else:
        return str(value)
    
    print(f'value confused us: {value} {type(value)}')
    return None

  def unpack_array(self, value: h5py.Dataset) -> str:
    """
    Unpack HDF5 arrays into strings that can be shown.
    """
    result = ""
    for f in value:
      if len(result) > 0:
        result = f'{result}, {f}'
      else:
        result = f'{f}'
    return f'[{result}]'

  def attributes(self, name: str) -> bool:
    """
    Step through the attributes for the node, add them to the dictionary.
    """
    data = self.file[name]
    if isinstance(data, (h5py.Dataset, h5py.Group)):
      for (key, value) in data.attrs.items():
        v = self.type_dispatch(value)
        if v is not None:
          path = f'{name}/{key}*'
          self.file_dict[path] = v

  def visit_entry(self, name: str) -> None:
    data = self.file[name]
    self.attributes(name)
    if isinstance(data, h5py.Dataset):
      if data.len() == 1:
        # Handle the simple cases.
        value = self.type_dispatch(data[0])
        if value is not None:
          self.file_dict[name] = value
      elif data.len() <= 16:
        # Unpack "small" arrays and show their contents
        value = self.unpack_array(data)
        if value is not None:
          self.file_dict[name] = value
      else:
        # This is where the bigger data sets remain
        if isinstance(data, (h5py.Dataset)):
          self.file_dict[name] = f'Large Dataset ({data.len()} elements)'
      self.count += 1

  def parse_header_as_dict(self, filepath: Path) -> dict:
    """
    Description:

    Parameters
    ----------
    filepath
        The path to the HDF5 file to be parsed

    Returns
    -------
    Dictionary
        A dictionary containing the header information
    
    Example
    -------
    ```
    parser = H5Parser()
    parser.parse_header_as_dict('/some/path/to/a/file.h5')
    ```
    """
    # Check our file exists before trying to open it!
    if os.path.isfile(filepath):
      self.file = h5py.File(filepath, 'r')
      self.file.visit(self.visit_entry)

    return self.file_dict

