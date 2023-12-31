from fastapi import FastAPI


class URLReverser:
    def __init__(self, app: FastAPI) -> None:
        self.app = app

    def reverse(self, name: str, **path_params) -> str:
        for route in self.app.routes:
            if route.name == name:
                return route.path.format(**path_params)
        raise KeyError(f'Route with name {name} not found')
