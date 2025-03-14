# **TGToolz – Telegram Bot Developer toolkit 🛠️**

**TGToolz** is a command-line utility designed to streamline **Telegram bot development** with the **Telegrinder** framework. Currently, it features an **i18n parser and code generator**, allowing developers to manage multilingual bot responses effortlessly. Future versions will introduce **bot scaffolding, prebuilt nodes, and built-in utilities** for faster development.

---

## ✨ **Features**

✅ **Advanced i18n Support** – Uses an **extended JSON format** with variables, gender-based text, pluralization, and inline formatting.
✅ **Code Generation** – Converts i18n JSON into structured **Telegrinder-ready Python classes**.
✅ **Validation** – Checks translation integrity and highlights missing or inconsistent keys.
✅ **Bot Templates (Coming Soon)** – Generate complete bot projects with a single command.
✅ **Prebuilt nodes (Coming Soon)** – Built-in **nodes** for cleaner and more scalable bot architecture.

---

## 📦 **Installation**

```sh
pip install tgtoolz
```

---

## 🚀 **Usage**

### 🔧 **Generate i18n Code**

Convert JSON translations into Python classes:
```sh
tgtoolz i18n refresh
```
---

## 📜 **Enhanced JSON Format for i18n**

TGToolz extends JSON with support for:
🔹 **Placeholders** – `{name:str}`, `{age:int}`
🔹 **Gender-based text** – `@gender(male, female, other)`
🔹 **Pluralization** – `@plural(one, few, many)`
🔹 **Rich Formatting** – `@bold(text)`, `@link(text, url)`, `@italic(text)`, etc

```json
{
  "MainI18N": {
    "hello": {
      "ru": "@bold(Привет!)\nТебя зовут {name:str}, тебе {age:int}.\n@link(Мои ресурсы, http://telegram.com).",
      "en": "@bold(Hello!)\nYour name is {name:str}, you are {age:int}.\n@link(My resources, http://telegram.com)"
    },
    "friends_count": {
      "ru": "Привет, @gender(мальчик, девочка, нейтральный), у тебя @bold({count:int}) @plural(друг, друга, друзей).",
      "en": "Hello, @gender(male, female, neutral), you have @bold({count:int}) @plural(friend, friends)."
    }
  }
}
```

---

## 🏆 **Generated Python Code**

After running `tgtoolz i18n refresh`, TGToolz creates a structured Python module (you should specify path for generated code in your pyproject.toml).

```toml
[tool.tgtoolz.i18n]
localization_file = "locales.json"
output_file = "src/i18n.py"
```

---

## ⚡ **Integrating TGToolz i18n in a Telegrinder Bot**

Using TGToolz with **Telegrinder** is simple:

```python
from telegrinder import Telegrinder, Message, HTMLFormatter
from telegrinder.node import Source
from telegrinder.rules import Text
from bot.i18n import MainI18N

bot = Telegrinder("TOKEN")

@bot.on.message(Text("hello"))
async def hello(message: Message, source: Source, i18n: MainI18N):
    await source.send(
        i18n.hello(name="Viktor", age=15),
        parse_mode=HTMLFormatter.PARSE_MODE
    )

bot.run_forever(skip_updates=True)
```
💡 **Now your bot responds dynamically based on user input and selected language!**

---

## 🔮 **Upcoming Features**

🚀 **Bot Templates** – Generate different bot types in seconds.
🛠 **Nodes** – Prebuilt components for structured development.
💾 **Middleware & Storage Integration** – Simplify session and API management.
🔌 **Plugin System** – Extend TGToolz with custom modules.

---

## 📜 **License**

TGToolz is licensed under the **MIT License** – Open-source and free to use.

---
