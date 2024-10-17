import logging
import logging.config
import os

path = os.path.abspath(__file__)
BASE_DIR = os.path.dirname(os.path.dirname(path))


class logger(object):
    def __init__(self,base_dir):
        logging_config = {
            # 必选项，其值是一个整数值，表示配置格式的版本，当前唯一可用的值就是1
            'version': 1,
            # 是否禁用现有的记录器
            'disable_existing_loggers': False,

            # 过滤器
            # 'filters': {
            #     'require_debug_true': {
            #         '()': RequireDebugTrue,  # 在开发环境，我设置DEBUG为True；在客户端，我设置DEBUG为False。从而控制是否需要使用某些处理器。
            #     }
            # },

            # 日志格式集合
            'formatters': {
                'simple': {
                    'format': '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s',
                },
            },

            # 处理器集合
            'handlers': {
                # 输出到控制台
                'console': {
                    'level': 'DEBUG',  # 输出信息的最低级别
                    'class': 'logging.StreamHandler',
                    'formatter': 'simple',  # 使用standard格式
                    # 'filters': ['require_debug_true', ]
                },
                # 输出到文件
                'log': {
                    'level': 'DEBUG',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'simple',
                    #'filename': os.path.join(BASE_DIR + "\\log", 'info.log'),  # 输出位置
                    'filename': os.path.join(base_dir, 'info.log'),  # 输出位置
                    'maxBytes': 1024 * 1024 * 5,  # 文件大小 5M
                    'backupCount': 5,  # 备份份数
                    'encoding': 'utf8',  # 文件编码
                },
            },

            # 日志管理器集合
            'loggers': {
                'root': {
                    'handlers': ['console', 'log'],
                    'level': 'DEBUG',
                    'propagate': True,  # 是否传递给父记录器
                },
                'simple': {
                    'handlers': ['console', 'log'],
                    'level': 'WARN',
                    'propagate': True,  # 是否传递给父记录器,
                }
            }
        }

        logging.config.dictConfig(logging_config)
        self.logger = logging.getLogger('root')
