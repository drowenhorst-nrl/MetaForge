from __future__ import annotations
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import json
from typing import List

from ezmetadataentry import EzMetadataEntry

@dataclass_json
@dataclass
class EzMetadataModel:
    entries: List[EzMetadataEntry] = field(default_factory=list)
    original_data_file: str = ''
    template_version: str = '1.0'

    @staticmethod
    def create_model(model_dict: dict, data_file_path: str, source_type: EzMetadataEntry.SourceType) -> EzMetadataModel:
        model = EzMetadataModel([], original_data_file=data_file_path)
        EzMetadataModel._add_model_entry(model_dict, '', model, source_type)
        return model

    @staticmethod
    def _add_model_entry(item, parent_path: str, model: EzMetadataModel, source_type: EzMetadataEntry.SourceType):
        for key, value in item.items():
            if type(value) is dict:
                new_parent_path = parent_path + key + '/'
                EzMetadataModel._add_model_entry(value, new_parent_path, model, source_type)
            else:
                item_path = parent_path + key
                if value is None:
                    value = ''
                metadata_entry = EzMetadataEntry(source_path=item_path,
                                                source_value=value,
                                                source_type=source_type,
                                                ht_name=key,
                                                ht_value='',
                                                ht_annotation='',
                                                ht_units='')
                model.append(metadata_entry)

    def append(self, entry: EzMetadataEntry):
        self.entries.append(entry)
    
    def insert(self, entry: EzMetadataEntry, index: int):
        self.entries.insert(index, entry)
    
    def remove(self, entry: EzMetadataEntry):
        if len(self.entries) > 0:
            self.entries.remove(entry)
            return True
        return False

    def remove_by_index(self, index: int):
        if len(self.entries) > 0:
            del self.entries[index]
            return True
        return False
    
    def remove_last(self) -> bool:
        if len(self.entries) > 0:
            del self.entries[-1]
            return True
        return False
    
    def remove_first(self) -> bool:
        if len(self.entries) > 0:
            del self.entries[0]
            return True
        return False
    
    def entry(self, index: int) -> EzMetadataEntry:
        return self.entries[index]

    def to_json_file(self, file_path: str, indent: int = 4):
        json_string = self.to_json_string(indent=indent)
        with open(file_path, 'w') as outfile:
            outfile.write(json_string)

    def to_json_string(self, indent: int = 4):
        return self.to_json(indent=indent)
    
    @staticmethod
    def from_json_file(file_path: str) -> EzMetadataModel:
        with open(file_path) as json_file:
            json_string = json.load(json_file)
            return EzMetadataModel.from_json_string(json_string)

    @staticmethod
    def from_json_string(json_string: str) -> EzMetadataModel:
        return EzMetadataModel.from_json(json_string)
