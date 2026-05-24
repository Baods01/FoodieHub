# Tortoise ORM 配置（用于 aerich）
TORTOISE_ORM = {
    "connections": {
        "default": "mysql://root:123456@localhost:3306/foodiehub_test"
    },
    "apps": {
        "models": {
            "models": ["models", "aerich.models"],
            "default_connection": "default",
        },
    },
}