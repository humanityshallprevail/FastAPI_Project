import pytest
from fastapi.testclient import TestClient
from app.main import app
import os

DATABASE_URL = os.getenv("DATABASE_URL")
client = TestClient(app)


def test_crud_menu_and_submenus():
    # Create menu
    test_menu = {"title": "Test Menu", "description": "This is a test menu"}
    response = client.post("/api/v1/menus", json=test_menu)
    assert response.status_code == 201
    menu_id = response.json()["id"]
    assert "id" in response.json()
    assert response.json()["title"] == test_menu["title"]



    # Get the created menu
    response = client.get(f"/api/v1/menus/{menu_id}")
    assert response.status_code == 200
    assert response.json()["id"] == menu_id

    # Create submenus
    test_submenu = {"title": "Test Submenu", "description": "This is a test submenu"}
    for i in range(3):
        response = client.post(f"/api/v1/menus/{menu_id}/submenus", json=test_submenu)
        assert response.status_code == 201
        # Create dishes for the submenu
        submenu_id = response.json()["id"]
        test_dish = {"title": f"Test Dish {i}", "description": f"This is test dish {i}", "price": "9.99"}
        for j in range(2):  # assuming each submenu has 2 dishes
            response = client.post(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes", json=test_dish)
            assert response.status_code == 201
            dish_id = response.json()["id"]

# -------------------------
    # Check that the number of submenus is correct
    response = client.get(f"/api/v1/menus/{menu_id}/submenus")
    assert response.status_code == 200
    assert len(response.json()) == 3

    # Check that the number of dishes is correct
    response = client.get(f"/api/v1/menus/{menu_id}/submenus/{response.json()[0]['id']}/dishes")
    assert response.status_code == 200
    assert len(response.json()) == 2

# -------------------------

    # Update a dish
    updated_dish = {"title": "Updated Dish", "description": "This is an updated test dish", "price": "12.99"}
    response = client.patch(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}", json=updated_dish)
    assert response.status_code == 200
    assert response.json()["title"] == updated_dish["title"]

    # Delete a dish
    response = client.delete(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Dish deleted"

    # Check that the dish no longer exists
    response = client.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}")
    assert response.status_code == 404
    # Update a submenu
    updated_submenu = {"title": "Updated Submenu", "description": "This is an updated test submenu"}
    response = client.patch(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}", json=updated_submenu)
    assert response.status_code == 200
    assert response.json()["title"] == updated_submenu["title"]

    # Delete a submenu
    response = client.delete(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "submenu deleted"

    # Check that the submenu no longer exists
    response = client.get(f"/api/v1/menus/{menu_id}/submenus/{submenu_id}")
    assert response.status_code == 404


# -------------------
    # Update menu
    updated_menu = {"title": "Updated Menu", "description": "This is an updated test menu"}
    response = client.patch(f"/api/v1/menus/{menu_id}", json=updated_menu)
    assert response.status_code == 200
    assert response.json()["title"] == updated_menu["title"]

    # Delete menu
    response = client.delete(f"/api/v1/menus/{menu_id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Menu deleted"

    # Check that the menu no longer exists
    response = client.get(f"/api/v1/menus/{menu_id}")
    assert response.status_code == 404







