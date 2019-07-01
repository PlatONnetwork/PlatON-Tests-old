from optparse import OptionParser


def parse_options():
    parser = OptionParser('PlatONTest')

    parser.add_option(
        '-U', '--url',
        dest='url',
        default=None,
        help='下载包路径，若不下载,则使用./deploy/rely/bin中的二进制文件'
    )

    parser.add_option(
        '-N', '--node',
        dest='node',
        default=None,
        help='测试节点配置文件路径'
    )

    parser.add_option(
        '-T', '--type',
        dest='type',
        default=None,
        help='测试类型,只能是all,pangu,ppos,exclude_ppos,exclude_vc'
    )

    parser.add_option(
        '-M', '--module',
        dest='module',
        default=None,
        help='测试模块，只能是transaction，contract，ppos，blockchain，consensus,vc,如果有多个，用“,”分割'
    )

    parser.add_option(
        '-C', '--case',
        dest='case',
        default=None,
        help='用例集，输入需要测试的用例'
    )
    opts, _ = parser.parse_args()
    return opts
