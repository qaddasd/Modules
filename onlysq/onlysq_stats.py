# meta developer: @qynon
# meta desc: Module for OnlySq API statistics. Get request counts and models info.

import logging
import aiohttp
import asyncio
import re
from telethon.tl.types import Message

from .. import loader, utils

logger = logging.getLogger(__name__)

__version__ = "1.0.5"
MODULE_URL = "https://raw.githubusercontent.com/qaddasd/Modules/main/onlysq/onlysq_stats.py"


@loader.tds
class OnlySqStatsMod(loader.Module):
    """Module for OnlySq API statistics. Get request counts and models info."""

    strings = {
        "name": "OnlySqStats",
        "loading": "<emoji document_id=5310093785313453924>⏳</emoji> <b>Loading statistics...</b>",
        "stats": (
            "<emoji document_id=5371037748188879474>📊</emoji> <b>OnlySq API Statistics</b>\n\n"
            "<emoji document_id=5294170562810862128>📅</emoji> <b>Today:</b> <code>{today}</code>\n"
            "<emoji document_id=5312076921254735498>📆</emoji> <b>This week:</b> <code>{week}</code>\n"
            "<emoji document_id=5314636966498763639>🗓</emoji> <b>This month:</b> <code>{month}</code>\n"
            "<emoji document_id=5316786826698978836>📈</emoji> <b>Total:</b> <code>{all}</code>"
        ),
        "today": "<emoji document_id=5294170562810862128>📅</emoji> <b>Requests today:</b> <code>{count}</code>",
        "week": "<emoji document_id=5312076921254735498>📆</emoji> <b>Requests this week:</b> <code>{count}</code>",
        "month": "<emoji document_id=5314636966498763639>🗓</emoji> <b>Requests this month:</b> <code>{count}</code>",
        "all": "<emoji document_id=5316786826698978836>📈</emoji> <b>Total requests:</b> <code>{count}</code>",
        "models": (
            "<emoji document_id=5372981976804366741>🤖</emoji> <b>OnlySq AI Models</b>\n\n"
            "<emoji document_id=5373141891321699086>📦</emoji> <b>Total models:</b> <code>{total}</code>\n"
            "<emoji document_id=5372926953978341366>✅</emoji> <b>Working:</b> <code>{working}</code>\n"
            "<emoji document_id=5372603421692408823>⚠️</emoji> <b>Unstable:</b> <code>{unstable}</code>\n"
            "<emoji document_id=5372926858986475400>❌</emoji> <b>Not working:</b> <code>{not_working}</code>\n\n"
            "<emoji document_id=5371123633498496106>🔧</emoji> <b>API Version:</b> <code>{version}</code>"
        ),
        "error": "<emoji document_id=5372926858986475400>🚫</emoji> <b>Error:</b> <code>{}</code>",
        "loaded": (
            "🌘 <b>Module OnlySqStats loaded</b> ʕ•ᴥ•ʔ\n"
            "ℹ️ 📊 OnlySq API statistics and AI models info\n\n"
            "▫️ <code>.sq</code> — Show request statistics\n"
            "▫️ <code>.sqmodels</code> — Show AI models info\n"
            "▫️ <code>.squpdate</code> — Check for updates\n\n"
            "📦 Version: <code>{version}</code>\n"
            "🫶 Developer: @qynon"
        ),
        "update_available": (
            "<emoji document_id=5316786826698978836>🔄</emoji> <b>Update available!</b>\n\n"
            "📦 Current: <code>{current}</code>\n"
            "🆕 New: <code>{new}</code>\n\n"
            "Use <code>.squpdate install</code> to update"
        ),
        "no_update": "<emoji document_id=5372926953978341366>✅</emoji> <b>You have the latest version:</b> <code>{version}</code>",
        "checking_update": "<emoji document_id=5310093785313453924>⏳</emoji> <b>Checking for updates...</b>",
        "installing": "<emoji document_id=5310093785313453924>⏳</emoji> <b>Installing update...</b>\n\n{progress}",
        "install_done": "<emoji document_id=5372926953978341366>✅</emoji> <b>Update installed successfully!</b>",
        "install_error": "<emoji document_id=5372926858986475400>❌</emoji> <b>Installation error:</b> <code>{}</code>",
        "graph_header": "<emoji document_id=5371037748188879474>📊</emoji> <b>OnlySq API — Request Graph</b>",
        "graph_today": "Today",
        "graph_week": "Week",
        "graph_month": "Month",
        "graph_total": "Total",
    }

    strings_ru = {
        "name": "OnlySqStats",
        "loading": "<emoji document_id=5310093785313453924>⏳</emoji> <b>Загрузка статистики...</b>",
        "stats": (
            "<emoji document_id=5371037748188879474>📊</emoji> <b>Статистика OnlySq API</b>\n\n"
            "<emoji document_id=5294170562810862128>📅</emoji> <b>Сегодня:</b> <code>{today}</code>\n"
            "<emoji document_id=5312076921254735498>📆</emoji> <b>За неделю:</b> <code>{week}</code>\n"
            "<emoji document_id=5314636966498763639>🗓</emoji> <b>За месяц:</b> <code>{month}</code>\n"
            "<emoji document_id=5316786826698978836>📈</emoji> <b>Всего:</b> <code>{all}</code>"
        ),
        "today": "<emoji document_id=5294170562810862128>📅</emoji> <b>Запросов сегодня:</b> <code>{count}</code>",
        "week": "<emoji document_id=5312076921254735498>📆</emoji> <b>Запросов за неделю:</b> <code>{count}</code>",
        "month": "<emoji document_id=5314636966498763639>🗓</emoji> <b>Запросов за месяц:</b> <code>{count}</code>",
        "all": "<emoji document_id=5316786826698978836>📈</emoji> <b>Всего запросов:</b> <code>{count}</code>",
        "models": (
            "<emoji document_id=5372981976804366741>🤖</emoji> <b>AI Модели OnlySq</b>\n\n"
            "<emoji document_id=5373141891321699086>📦</emoji> <b>Всего моделей:</b> <code>{total}</code>\n"
            "<emoji document_id=5372926953978341366>✅</emoji> <b>Работают:</b> <code>{working}</code>\n"
            "<emoji document_id=5372603421692408823>⚠️</emoji> <b>Нестабильны:</b> <code>{unstable}</code>\n"
            "<emoji document_id=5372926858986475400>❌</emoji> <b>Не работают:</b> <code>{not_working}</code>\n\n"
            "<emoji document_id=5371123633498496106>🔧</emoji> <b>Версия API:</b> <code>{version}</code>"
        ),
        "error": "<emoji document_id=5372926858986475400>🚫</emoji> <b>Ошибка:</b> <code>{}</code>",
        "loaded": (
            "🌘 <b>Модуль OnlySqStats загружен</b> ʕ•ᴥ•ʔ\n"
            "ℹ️ 📊 Статистика OnlySq API и информация о AI моделях\n\n"
            "▫️ <code>.sq</code> — Показать статистику запросов\n"
            "▫️ <code>.sqmodels</code> — Показать информацию о моделях\n"
            "▫️ <code>.squpdate</code> — Проверить обновления\n\n"
            "📦 Версия: <code>{version}</code>\n"
            "🫶 Разработчик: @qynon"
        ),
        "update_available": (
            "<emoji document_id=5316786826698978836>🔄</emoji> <b>Доступно обновление!</b>\n\n"
            "📦 Текущая: <code>{current}</code>\n"
            "🆕 Новая: <code>{new}</code>\n\n"
            "Используй <code>.squpdate install</code> для обновления"
        ),
        "no_update": "<emoji document_id=5372926953978341366>✅</emoji> <b>У тебя последняя версия:</b> <code>{version}</code>",
        "checking_update": "<emoji document_id=5310093785313453924>⏳</emoji> <b>Проверка обновлений...</b>",
        "installing": "<emoji document_id=5310093785313453924>⏳</emoji> <b>Установка обновления...</b>\n\n{progress}",
        "install_done": "<emoji document_id=5372926953978341366>✅</emoji> <b>Обновление успешно установлено!</b>",
        "install_error": "<emoji document_id=5372926858986475400>❌</emoji> <b>Ошибка установки:</b> <code>{}</code>",
        "graph_header": "<emoji document_id=5371037748188879474>📊</emoji> <b>OnlySq API — График запросов</b>",
        "graph_today": "Сегодня",
        "graph_week": "Неделя",
        "graph_month": "Месяц",
        "graph_total": "Всего",
        "_cls_doc": "Модуль для статистики OnlySq API. Показывает количество запросов и информацию о моделях.",
    }

    def __init__(self):
        self.base_url = "https://api.onlysq.ru"

    async def on_dlmod(self):
        await self.inline.bot.send_message(
            self._tg_id,
            self.strings["loaded"].format(version=__version__),
        )
        
        try:
            new_version = await self._get_remote_version()
            if new_version and self._compare_versions(new_version, __version__) > 0:
                await self.inline.bot.send_message(
                    self._tg_id,
                    self.strings["update_available"].format(
                        current=__version__,
                        new=new_version,
                    ),
                )
        except Exception:
            pass

    async def _get_remote_version(self) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(MODULE_URL) as response:
                    if response.status == 200:
                        content = await response.text()
                        match = re.search(r'__version__\s*=\s*["\']([\d.]+)["\']', content)
                        if match:
                            return match.group(1)
        except Exception:
            pass
        return None

    def _compare_versions(self, v1: str, v2: str) -> int:
        v1_parts = [int(x) for x in v1.split(".")]
        v2_parts = [int(x) for x in v2.split(".")]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            p1 = v1_parts[i] if i < len(v1_parts) else 0
            p2 = v2_parts[i] if i < len(v2_parts) else 0
            if p1 > p2:
                return 1
            elif p1 < p2:
                return -1
        return 0

    def _create_progress_bar(self, progress: int, total: int = 100) -> str:
        filled = int(20 * progress / total)
        empty = 20 - filled
        bar = "█" * filled + "░" * empty
        return f"<code>[{bar}]</code> {progress}%"

    async def _animate_progress(self, message, stages: list):
        for i, (progress, text) in enumerate(stages):
            bar = self._create_progress_bar(progress)
            await utils.answer(
                message,
                self.strings["installing"].format(progress=f"{bar}\n\n<i>{text}</i>"),
            )
            await asyncio.sleep(0.5)

    async def _fetch_count(self, session: aiohttp.ClientSession, endpoint: str) -> int:
        async with session.get(f"{self.base_url}/crawler/{endpoint}") as response:
            data = await response.json()
            return data.get("count", 0)

    def _format_number(self, num: int) -> str:
        return f"{num:,}".replace(",", " ")

    @loader.command(
        ru_doc="Показать всю статистику запросов OnlySq API",
        en_doc="Show all OnlySq API request statistics",
    )
    async def sq(self, message: Message):
        await utils.answer(message, self.strings["loading"])

        try:
            async with aiohttp.ClientSession() as session:
                today = await self._fetch_count(session, "today")
                week = await self._fetch_count(session, "week")
                month = await self._fetch_count(session, "month")
                all_time = await self._fetch_count(session, "all")

            await utils.answer(
                message,
                self.strings["stats"].format(
                    today=self._format_number(today),
                    week=self._format_number(week),
                    month=self._format_number(month),
                    all=self._format_number(all_time),
                ),
            )
        except Exception as e:
            logger.exception("Failed to fetch OnlySq stats")
            await utils.answer(message, self.strings["error"].format(str(e)))

    @loader.command(
        ru_doc="Показать количество запросов за сегодня",
        en_doc="Show today's request count",
    )
    async def sqtoday(self, message: Message):
        await utils.answer(message, self.strings["loading"])

        try:
            async with aiohttp.ClientSession() as session:
                count = await self._fetch_count(session, "today")

            await utils.answer(
                message,
                self.strings["today"].format(count=self._format_number(count)),
            )
        except Exception as e:
            logger.exception("Failed to fetch OnlySq today stats")
            await utils.answer(message, self.strings["error"].format(str(e)))

    @loader.command(
        ru_doc="Показать количество запросов за неделю",
        en_doc="Show this week's request count",
    )
    async def sqweek(self, message: Message):
        await utils.answer(message, self.strings["loading"])

        try:
            async with aiohttp.ClientSession() as session:
                count = await self._fetch_count(session, "week")

            await utils.answer(
                message,
                self.strings["week"].format(count=self._format_number(count)),
            )
        except Exception as e:
            logger.exception("Failed to fetch OnlySq week stats")
            await utils.answer(message, self.strings["error"].format(str(e)))

    @loader.command(
        ru_doc="Показать количество запросов за месяц",
        en_doc="Show this month's request count",
    )
    async def sqmonth(self, message: Message):
        await utils.answer(message, self.strings["loading"])

        try:
            async with aiohttp.ClientSession() as session:
                count = await self._fetch_count(session, "month")

            await utils.answer(
                message,
                self.strings["month"].format(count=self._format_number(count)),
            )
        except Exception as e:
            logger.exception("Failed to fetch OnlySq month stats")
            await utils.answer(message, self.strings["error"].format(str(e)))

    @loader.command(
        ru_doc="Показать общее количество запросов",
        en_doc="Show total request count",
    )
    async def sqall(self, message: Message):
        await utils.answer(message, self.strings["loading"])

        try:
            async with aiohttp.ClientSession() as session:
                count = await self._fetch_count(session, "all")

            await utils.answer(
                message,
                self.strings["all"].format(count=self._format_number(count)),
            )
        except Exception as e:
            logger.exception("Failed to fetch OnlySq all stats")
            await utils.answer(message, self.strings["error"].format(str(e)))

    @loader.command(
        ru_doc="Показать информацию о моделях OnlySq AI",
        en_doc="Show OnlySq AI models info",
    )
    async def sqmodels(self, message: Message):
        await utils.answer(message, self.strings["loading"])

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/ai/models") as response:
                    data = await response.json()

            models = data.get("models", {})
            version = data.get("api-version", "unknown")
            
            total = len(models)
            working = sum(1 for m in models.values() if m.get("status") == "work")
            unstable = sum(1 for m in models.values() if m.get("status") == "unstable")
            not_working = sum(1 for m in models.values() if m.get("status") == "not_work")

            await utils.answer(
                message,
                self.strings["models"].format(
                    total=total,
                    working=working,
                    unstable=unstable,
                    not_working=not_working,
                    version=version,
                ),
            )
        except Exception as e:
            logger.exception("Failed to fetch OnlySq models")
            await utils.answer(message, self.strings["error"].format(str(e)))

    @loader.command(
        ru_doc="Проверить обновления / установить обновление",
        en_doc="Check for updates / install update",
    )
    async def squpdate(self, message: Message):
        args = utils.get_args_raw(message)
        
        await utils.answer(message, self.strings["checking_update"])
        
        try:
            new_version = await self._get_remote_version()
            
            if not new_version:
                await utils.answer(message, self.strings["no_update"].format(version=__version__))
                return
            
            if self._compare_versions(new_version, __version__) <= 0:
                await utils.answer(message, self.strings["no_update"].format(version=__version__))
                return
            
            if args != "install":
                await utils.answer(
                    message,
                    self.strings["update_available"].format(
                        current=__version__,
                        new=new_version,
                    ),
                )
                return
            
            is_ru = "Загрузка" in str(self.strings.get("loading", ""))
            
            if is_ru:
                stages = [
                    (10, "Подключение к серверу..."),
                    (30, "Скачивание модуля..."),
                    (60, "Установка..."),
                    (90, "Перезагрузка..."),
                ]
            else:
                stages = [
                    (10, "Connecting to server..."),
                    (30, "Downloading module..."),
                    (60, "Installing..."),
                    (90, "Reloading..."),
                ]
            
            for progress, text in stages[:2]:
                bar = self._create_progress_bar(progress)
                await utils.answer(
                    message,
                    self.strings["installing"].format(progress=f"{bar}\n\n<i>{text}</i>"),
                )
                await asyncio.sleep(0.4)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(MODULE_URL) as response:
                    if response.status != 200:
                        raise Exception(f"HTTP {response.status}")
                    module_code = await response.text()
            
            for progress, text in stages[2:3]:
                bar = self._create_progress_bar(progress)
                await utils.answer(
                    message,
                    self.strings["installing"].format(progress=f"{bar}\n\n<i>{text}</i>"),
                )
                await asyncio.sleep(0.3)
            
            await self.allmodules.load_module(
                module_code,
                origin=MODULE_URL,
                save_fs=True,
            )
            
            bar = self._create_progress_bar(100)
            await utils.answer(
                message,
                self.strings["installing"].format(progress=f"{bar}\n\n<i>{'Готово!' if is_ru else 'Done!'}</i>"),
            )
            await asyncio.sleep(0.5)
            
            await utils.answer(message, self.strings["install_done"])
            
        except Exception as e:
            logger.exception("Failed to update module")
            await utils.answer(message, self.strings["install_error"].format(str(e)))

    def _create_bar_graph(self, value: int, max_value: int, width: int = 15) -> str:
        if max_value == 0:
            filled = 0
        else:
            filled = int(width * value / max_value)
        empty = width - filled
        return "█" * filled + "░" * empty

    @loader.command(
        ru_doc="Показать график запросов OnlySq API",
        en_doc="Show OnlySq API requests graph",
    )
    async def sqgraph(self, message: Message):
        await utils.answer(message, self.strings["loading"])

        try:
            async with aiohttp.ClientSession() as session:
                today = await self._fetch_count(session, "today")
                week = await self._fetch_count(session, "week")
                month = await self._fetch_count(session, "month")
                all_time = await self._fetch_count(session, "all")

            max_val = max(today, week, month, all_time)
            
            today_bar = self._create_bar_graph(today, max_val)
            week_bar = self._create_bar_graph(week, max_val)
            month_bar = self._create_bar_graph(month, max_val)
            all_bar = self._create_bar_graph(all_time, max_val)

            graph = (
                f"{self.strings['graph_header']}\n\n"
                f"<code>"
                f"{self.strings['graph_today']:>8} │{today_bar}│ {self._format_number(today)}\n"
                f"{self.strings['graph_week']:>8} │{week_bar}│ {self._format_number(week)}\n"
                f"{self.strings['graph_month']:>8} │{month_bar}│ {self._format_number(month)}\n"
                f"{self.strings['graph_total']:>8} │{all_bar}│ {self._format_number(all_time)}"
                f"</code>"
            )

            await utils.answer(message, graph)
        except Exception as e:
            logger.exception("Failed to fetch OnlySq graph")
            await utils.answer(message, self.strings["error"].format(str(e)))
