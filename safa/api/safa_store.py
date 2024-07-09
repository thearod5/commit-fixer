import json
from typing import Any, Dict, Optional

from safa.api.constants import STORE_ENTITIES
from safa.utils.fs import read_json_file

ProjectData = Dict


class SafaStore:

    def __init__(self, cache_file_path: Optional[str] = None):
        """
        Initializes store with optional file location to persist data across runs.
        :param cache_file_path: Path to file to store data in.
        """
        self.cache_file_path = cache_file_path
        self.project_data = self.__create_empty_data()
        self.__load_cache_file()

    def has(self, entity_type: str, entity_id: str, assert_has: bool = False) -> bool:
        """
        Checks whether given entity id exists in store.
        :param entity_type: The type of entity associated with ID.
        :param entity_id: ID of entity to check for.
        :param assert_has: Whether to throw error if entity does not exist.
        :return: True if entity exists in store.
        """
        self.__has_entity_type(entity_type, assert_has=True)
        contains_entity_id = entity_id in self.project_data[entity_type]
        if assert_has and not contains_entity_id:
            raise Exception(f"Entity data did not contain: {entity_id}")
        return contains_entity_id

    def get(self, entity_type: str, entity_id: str) -> Any:
        """
        Retrieves entity in project data.
        :param entity_type: The type of entity being retrieved.
        :param entity_id: The ID of the entity.
        :return: The entity.
        """
        print(f"...store retrieved {entity_type}...")
        return self.project_data[entity_type][entity_id]

    def save(self, entity_type: str, entity_id: str, entity_data: Dict) -> None:
        """
        Saves entity data in store.
        :param entity_type: The type of entity being saved.
        :param entity_id: The ID of entity.
        :param entity_data: The data being saved.
        :return: None
        """
        self.__has_entity_type(entity_type, assert_has=True)
        self.project_data[entity_type][entity_id] = entity_data
        self.__write_to_disk()

    def delete(self, entity_type: str, entity_id: str) -> None:
        """
        Deletes data associated to entity.
        :param entity_type: Type of entity.
        :param entity_id: ID of entity.
        :return: None
        """
        self.__has_entity_type(entity_type, assert_has=True)
        if entity_id not in self.project_data[entity_type]:
            return
        del self.project_data[entity_type][entity_id]
        self.__write_to_disk()

    def __write_to_disk(self) -> None:
        """
        Writes store data to cache location.
        :return: None
        """
        if self.cache_file_path is None:
            return
        with open(self.cache_file_path, "w") as f:
            f.write(json.dumps(self.project_data, indent=4))

    def __load_cache_file(self) -> None:
        """
        Loads data from cache file.
        :return: None
        """
        if self.cache_file_path is None:
            return
        json_data = read_json_file(self.cache_file_path)
        for entity_type in STORE_ENTITIES:
            cached_entity_data = json_data.get(entity_type, {})
            self.project_data[entity_type].update(cached_entity_data)

    @staticmethod
    def __has_entity_type(entity_type: str, assert_has: bool = False) -> bool:
        """
        Checks to see whether given entity type is valid.
        :param entity_type: The entity type to check.
        :param assert_has: Whether to throw exception if not found.
        :return: True if found, False otherwise.
        """
        entity_type_found = entity_type in STORE_ENTITIES
        if not entity_type_found and assert_has:
            expected_entities = ",".join(STORE_ENTITIES)
            raise Exception(f"Expected entity type ({entity_type}) to be one of {expected_entities}")
        return entity_type_found

    @staticmethod
    def __create_empty_data() -> Dict:
        """
        Initializes data with empty data for each registered entity type.
        :return: Project data.
        """
        return {k: {} for k in STORE_ENTITIES}
