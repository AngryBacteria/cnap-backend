from pydantic import BaseModel
import pytest
from helpers.DBHelper import DBHelper, CollectionName, get_nested_value


@pytest.mark.asyncio
async def test_db_collections() -> None:
    """Test that all collections defined in CollectionName exist and no others exist"""
    dbh = DBHelper.get_instance()

    # Get all actual collection names from the database
    actual_collections = await dbh.database.list_collection_names()
    actual_collections_set = set(actual_collections)

    # Get all expected collection names from the enum
    expected_collections = {name.value for name in CollectionName}

    # Check if all expected collections exist
    missing_collections = expected_collections - actual_collections_set
    assert not missing_collections, f"Missing collections: {missing_collections}"

    # Check if there are any unexpected collections
    extra_collections = actual_collections_set - expected_collections
    assert not extra_collections, f"Unexpected collections found: {extra_collections}"

    # Check if counts match
    assert len(actual_collections) == len(CollectionName), (
        f"Number of collections mismatch. Expected {len(CollectionName)}, "
        f"got {len(actual_collections)}"
    )


@pytest.mark.asyncio
async def test_get_nested_value() -> None:
    """Test that get_nested_value works correctly"""

    class InnerInnerModel(BaseModel):
        city: str

    class InnerModel(BaseModel):
        age: int
        details: InnerInnerModel

    class TestModel(BaseModel):
        name: str
        info: InnerModel

    test_dict = {"name": "test", "info": {"age": 25, "details": {"city": "New York"}}}
    test_model = TestModel.model_validate(test_dict)

    assert get_nested_value(test_model, "name") == "test"
    assert get_nested_value(test_model, "info.age") == 25
    assert get_nested_value(test_model, "info.details.city") == "New York"

    assert get_nested_value(test_dict, "name") == "test"
    assert get_nested_value(test_dict, "info.age") == 25
    assert get_nested_value(test_dict, "info.details.city") == "New York"


if __name__ == "__main__":
    pytest.main([__file__])
