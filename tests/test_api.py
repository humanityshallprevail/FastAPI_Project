import logging
import os

import httpx
import pytest

from app.main import app
from url_reverser import URLReverser  # Custom class defined in url_reverser in root dir

DATABASE_URL = os.getenv('DATABASE_URL')
logging.basicConfig(level=logging.DEBUG)


@pytest.mark.asyncio
async def test_endpoint() -> None:
    async with httpx.AsyncClient(app=app, base_url='http://localhost:8000') as client:
        reverser = URLReverser(app)
        url = reverser.reverse('get_item', item_id=42)
        response = await client.get(url)
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_crud_menu_and_submenus() -> None:
    async with httpx.AsyncClient(app=app, base_url='http://localhost:8000') as client:
        # Create menu
        test_menu = {'title': 'Test Menu', 'description': 'This is a test menu'}
        response = await client.post('/api/v1/menus', json=test_menu)
        assert response.status_code == 201
        menu_id = response.json()['id']
        assert 'id' in response.json()
        assert response.json()['title'] == test_menu['title']

        # Get the created menu
        response = await client.get(f'/api/v1/menus/{menu_id}')
        assert response.status_code == 200
        assert response.json()['id'] == menu_id

        # Create submenus
        test_submenu = {'title': 'Test Submenu', 'description': 'This is a test submenu'}
        for i in range(3):
            response = await client.post(f'/api/v1/menus/{menu_id}/submenus', json=test_submenu)
            assert response.status_code == 201
            # Create dishes for the submenu
            submenu_id = response.json()['id']
            test_dish = {'title': f'Test Dish {i}', 'description': f'This is test dish {i}', 'price': '9.99'}
            for j in range(2):  # assuming each submenu has 2 dishes
                response = await client.post(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes', json=test_dish)
                assert response.status_code == 201
                dish_id = response.json()['id']

    # -------------------------
        # Check that the number of submenus is correct
        response = await client.get(f'/api/v1/menus/{menu_id}/submenus')
        assert response.status_code == 200
        assert len(response.json()) == 3

        # Check that the number of dishes is correct
        response = await client.get(f"/api/v1/menus/{menu_id}/submenus/{response.json()[0]['id']}/dishes")
        assert response.status_code == 200
        assert len(response.json()) == 2

    # -------------------------

        response = await client.get('/api/v1/menu')
        assert response.status_code == 200
        menus = response.json()

        # Assuming only one menu has been created
        # assert len(menus) == 5

        # Verify the details of the menu
        menu = menus[0]
        assert menu['title'] == 'Test Menu'
        assert menu['description'] == 'This is a test menu'

        # Verify the number of submenus
        assert len(menu['submenus']) == 3
        k = 0
        # Iterate through the submenus to verify their details
        for submenu in menu['submenus']:
            assert submenu['title'] == 'Test Submenu'
            assert submenu['description'] == 'This is a test submenu'

            # Check the number of dishes in each submenu
            assert len(submenu['dishes']) == 2
            for i in range(2):

                assert submenu['dishes'][i]['title'] == f'Test Dish {k}'
            k += 1

    # -------------------------
        # Update a dish
        updated_dish = {'title': 'Updated Dish', 'description': 'This is an updated test dish', 'price': '12.99'}
        response = await client.patch(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}', json=updated_dish)
        assert response.status_code == 200
        assert response.json()['title'] == updated_dish['title']

        # Delete a dish
        response = await client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
        assert response.status_code == 200
        assert response.json()['message'] == 'Dish deleted'

        # Check that the dish no longer exists
        response = await client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}/dishes/{dish_id}')
        assert response.status_code == 404
        # Update a submenu
        updated_submenu = {'title': 'Updated Submenu', 'description': 'This is an updated test submenu'}
        response = await client.patch(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}', json=updated_submenu)
        assert response.status_code == 200
        assert response.json()['title'] == updated_submenu['title']

        # Delete a submenu
        response = await client.delete(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
        assert response.status_code == 200
        assert response.json()['message'] == 'submenu deleted'

        # Check that the submenu no longer exists
        response = await client.get(f'/api/v1/menus/{menu_id}/submenus/{submenu_id}')
        assert response.status_code == 404

    # -------------------
        # Update menu
        updated_menu = {'title': 'Updated Menu', 'description': 'This is an updated test menu'}
        response = await client.patch(f'/api/v1/menus/{menu_id}', json=updated_menu)
        assert response.status_code == 200
        assert response.json()['title'] == updated_menu['title']

        # Delete menu
        response = await client.delete(f'/api/v1/menus/{menu_id}')
        assert response.status_code == 200
        assert response.json()['message'] == 'Menu deleted'

        # Check that the menu no longer exists
        response = await client.get(f'/api/v1/menus/{menu_id}')
        assert response.status_code == 404
