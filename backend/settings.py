TORTOISE_ORM = {
            'connections': {
                'default': {
                    'engine': 'tortoise.backends.mysql',
                    'credentials': {
                        'host': '127.0.0.1',
                        'port': '3306',
                        'user':'root',
                        'password':'123456',
                        'database':'foodie_hub',
                        'minsize': 1,
                        'maxsize': 5,
                        'charset':'utf8mb4',
                        'echo': True,
                    }
                },
            },
            'apps': {
                'models': {
                    'models': [
                        'models.base',
                        'models.users',
                        'models.shops',
                        'models.categories',
                        'models.dining_methods',
                        'models.ratings',
                        'models.comments',
                        'models.menu_items',
                        'models.images',
                        'models.favorites',
                        'models.messages',
                        'models.shop_edit_requests',
                        'models.user_behavior_logs',
                        'aerich.models',
                        ],
                    'default_connection': 'default',
                }
            },
            'use_tz': False,
            'timezone': 'Asia/Shanghai'
}
