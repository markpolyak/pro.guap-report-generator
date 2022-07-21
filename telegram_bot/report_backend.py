from typing import Any, Union

import httpx
import re

from io import BytesIO


class ReportBackend:
    """Организует доступ к бэкенду.
    После замены тестового бэкенда на реализованный в рамках задания №3,
    Будет необходимо незначительно отредактировать данный класс."""

    def __init__(self, base_url: str):
        self.__base_url = base_url

    async def check_token(self, token: str) -> bool:
        try:
            await self.fetch_semesters(token)
            return True
        except UnauthorizedError:
            return False

    async def fetch_semesters(self, token: str) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.__base_url + '/semesters',
                headers={'Authorization': token}
            )

            if response.status_code == 401:
                raise UnauthorizedError

            return response.json()

    async def fetch_subjects(self, token: str, semester_id: Union[str, int]) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.__base_url}/subjects/{semester_id}',
                headers={'Authorization': token}
            )

            if response.status_code == 401:
                raise UnauthorizedError

            return response.json()

    async def fetch_reports(self, token: str, semester_id: Union[str, int], subject_id: Union[str, int]) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.__base_url}/reports/{semester_id}/{subject_id}',
                headers={'Authorization': token}
            )

            if response.status_code == 401:
                raise UnauthorizedError

            return response.json()

    async def download_report(
            self,
            token: str,
            semester_id: Union[str, int],
            subject_id: Union[str, int],
            report_id: Union[str, int]
    ) -> BytesIO:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f'{self.__base_url}/report/{semester_id}/{subject_id}/{report_id}',
                headers={'Authorization': token}
            )

            if response.status_code == 401:
                raise UnauthorizedError

            file = BytesIO(response.content)

            match = re.search(r'filename="(.+)"|filename=(\S+)', response.headers['content-disposition'])
            if match is not None:
                file.name = match.group(1) or match.group(2)
            else:
                file.name = 'unknown'

            print(f'{response.headers["content-disposition"]=} {file.name=}')

            return file


class UnauthorizedError(Exception):
    def __init__(self):
        pass
