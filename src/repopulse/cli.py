"""
CLI入口模块 - CLI entry point module.

使用argparse构建命令行接口，支持多个子命令。
Builds CLI interface using argparse with multiple subcommands.
"""

import argparse
import sys
from typing import List, Optional

from . import __version__
from .config import Config
from .core import RepositoryManager
from .api import GitHubAPI, APIError, RateLimitError
from .health import HealthEngine
from .tags import TagEngine
from .search import SearchFilter
from .batch import BatchOperator
from .deps import DependencyChecker
from .tui import Dashboard


def create_parser() -> argparse.ArgumentParser:
    """创建CLI参数解析器。

    Create CLI argument parser.

    Returns:
        配置好的ArgumentParser实例. Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="repopulse",
        description="RepoPulse - 轻量级Git仓库智能管理TUI引擎",
        epilog="示例: repopulse dashboard --user octocat",
    )
    parser.add_argument(
        "-V", "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="可用命令",
        description="RepoPulse支持的子命令",
    )

    # ==================== dashboard 命令 ====================
    dash_parser = subparsers.add_parser(
        "dashboard",
        help="启动交互式TUI仪表盘",
        description="启动交互式TUI仪表盘，展示仓库概览、健康评分和标签统计",
    )
    dash_parser.add_argument(
        "--user", "-u",
        type=str,
        default=None,
        help="GitHub用户名或组织名（默认使用认证用户）",
    )
    dash_parser.add_argument(
        "--sort", "-s",
        type=str,
        default="updated",
        choices=["updated", "created", "pushed", "full_name"],
        help="仓库排序方式（默认: updated）",
    )

    # ==================== list 命令 ====================
    list_parser = subparsers.add_parser(
        "list",
        help="列出仓库",
        description="列出用户/组织的仓库列表",
    )
    list_parser.add_argument(
        "--user", "-u",
        type=str,
        default=None,
        help="GitHub用户名或组织名",
    )
    list_parser.add_argument(
        "--sort", "-s",
        type=str,
        default="updated",
        choices=["updated", "created", "pushed", "full_name"],
        help="排序方式（默认: updated）",
    )
    list_parser.add_argument(
        "--limit", "-l",
        type=int,
        default=20,
        help="显示数量限制（默认: 20）",
    )
    list_parser.add_argument(
        "--export", "-e",
        type=str,
        default=None,
        help="导出文件路径（支持.json和.csv）",
    )

    # ==================== health 命令 ====================
    health_parser = subparsers.add_parser(
        "health",
        help="查看仓库健康评分",
        description="查看仓库的健康评分报告",
    )
    health_parser.add_argument(
        "--user", "-u",
        type=str,
        default=None,
        help="GitHub用户名或组织名",
    )
    health_parser.add_argument(
        "--repo", "-r",
        type=str,
        default=None,
        help="指定仓库（格式: owner/repo）",
    )
    health_parser.add_argument(
        "--detailed", "-d",
        action="store_true",
        default=False,
        help="显示详细评分信息",
    )

    # ==================== search 命令 ====================
    search_parser = subparsers.add_parser(
        "search",
        help="搜索与过滤仓库",
        description="按条件搜索和过滤仓库",
    )
    search_parser.add_argument(
        "query",
        type=str,
        nargs="?",
        default="",
        help="搜索关键词",
    )
    search_parser.add_argument(
        "--user", "-u",
        type=str,
        default=None,
        help="在指定用户的仓库中搜索",
    )
    search_parser.add_argument(
        "--language", "-l",
        type=str,
        default=None,
        help="按编程语言过滤",
    )
    search_parser.add_argument(
        "--min-stars",
        type=int,
        default=None,
        help="最小Stars数",
    )
    search_parser.add_argument(
        "--max-stars",
        type=int,
        default=None,
        help="最大Stars数",
    )
    search_parser.add_argument(
        "--min-forks",
        type=int,
        default=None,
        help="最小Forks数",
    )
    search_parser.add_argument(
        "--updated-within",
        type=int,
        default=None,
        metavar="DAYS",
        help="在N天内更新过",
    )
    search_parser.add_argument(
        "--sort-by",
        type=str,
        default="stars",
        choices=["stars", "forks", "updated", "name", "health", "issues"],
        help="排序字段（默认: stars）",
    )
    search_parser.add_argument(
        "--github",
        action="store_true",
        default=False,
        help="使用GitHub API搜索（而非本地过滤）",
    )

    # ==================== tags 命令 ====================
    tags_parser = subparsers.add_parser(
        "tags",
        help="查看智能标签",
        description="查看仓库的智能标签分类",
    )
    tags_parser.add_argument(
        "--user", "-u",
        type=str,
        default=None,
        help="GitHub用户名或组织名",
    )
    tags_parser.add_argument(
        "--list-all",
        action="store_true",
        default=False,
        help="列出所有可用标签及其描述",
    )

    # ==================== batch 命令 ====================
    batch_parser = subparsers.add_parser(
        "batch",
        help="批量操作",
        description="批量操作仓库（Star/Unstar/导出）",
    )
    batch_parser.add_argument(
        "action",
        type=str,
        choices=["star", "unstar", "export"],
        help="操作类型: star, unstar, export",
    )
    batch_parser.add_argument(
        "--user", "-u",
        type=str,
        default=None,
        help="GitHub用户名或组织名",
    )
    batch_parser.add_argument(
        "--repos", "-r",
        type=str,
        nargs="+",
        default=None,
        help="指定仓库名称列表（格式: owner/repo）",
    )
    batch_parser.add_argument(
        "--filter-tag", "-t",
        type=str,
        default=None,
        help="按标签筛选要操作的仓库",
    )
    batch_parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="导出文件路径（export操作必需）",
    )
    batch_parser.add_argument(
        "--format", "-f",
        type=str,
        default="json",
        choices=["json", "csv"],
        help="导出格式（默认: json）",
    )

    # ==================== deps 命令 ====================
    deps_parser = subparsers.add_parser(
        "deps",
        help="依赖安全检查",
        description="检查依赖文件中的已知漏洞",
    )
    deps_parser.add_argument(
        "file",
        type=str,
        nargs="?",
        default=None,
        help="依赖文件路径（requirements.txt或package.json）",
    )
    deps_parser.add_argument(
        "--db-info",
        action="store_true",
        default=False,
        help="显示漏洞数据库信息",
    )

    # ==================== config 命令 ====================
    config_parser = subparsers.add_parser(
        "config",
        help="配置管理",
        description="管理RepoPulse配置",
    )
    config_parser.add_argument(
        "action",
        type=str,
        choices=["show", "set-token", "set-user"],
        nargs="?",
        default="show",
        help="配置操作",
    )
    config_parser.add_argument(
        "value",
        type=str,
        nargs="?",
        default=None,
        help="配置值",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI主入口函数。

    CLI main entry point.

    Args:
        argv: 命令行参数列表，为None时使用sys.argv。
              Command line arguments, uses sys.argv if None.

    Returns:
        退出码（0成功，非0失败）. Exit code (0 success, non-0 failure).
    """
    parser = create_parser()
    args = parser.parse_args(argv)

    # 没有子命令时显示帮助
    if not args.command:
        parser.print_help()
        return 0

    # 初始化配置
    config = Config()

    try:
        if args.command == "dashboard":
            return _cmd_dashboard(args, config)
        elif args.command == "list":
            return _cmd_list(args, config)
        elif args.command == "health":
            return _cmd_health(args, config)
        elif args.command == "search":
            return _cmd_search(args, config)
        elif args.command == "tags":
            return _cmd_tags(args, config)
        elif args.command == "batch":
            return _cmd_batch(args, config)
        elif args.command == "deps":
            return _cmd_deps(args, config)
        elif args.command == "config":
            return _cmd_config(args, config)
        else:
            parser.print_help()
            return 1

    except RateLimitError as e:
        console = Dashboard(config=config).console
        console.print(f"[bold red]API速率限制: {e}[/bold red]")
        console.print("[yellow]请稍后重试，或设置GitHub Token以提高速率限制。[/yellow]")
        return 2
    except APIError as e:
        console = Dashboard(config=config).console
        console.print(f"[bold red]API错误: {e}[/bold red]")
        if not config.github_token:
            console.print("[yellow]提示: 设置GitHub Token可以获得更高的API速率限制。[/yellow]")
            console.print("[yellow]  repopulse config set-token <your_token>[/yellow]")
        return 2
    except KeyboardInterrupt:
        print("\n操作已取消。")
        return 130
    except Exception as e:
        console = Dashboard(config=config).console
        console.print(f"[bold red]未知错误: {e}[/bold red]")
        return 1


def _cmd_dashboard(args: argparse.Namespace, config: Config) -> int:
    """处理dashboard子命令。

    Handle dashboard subcommand.
    """
    dashboard = Dashboard(config=config)
    console = dashboard.console

    # 显示加载提示
    with dashboard.show_loading("正在加载仓库数据..."):
        manager = RepositoryManager(config=config)
        try:
            manager.load_user_repos(
                username=args.user,
                sort=args.sort,
            )
        except APIError as e:
            console.print(f"[red]加载仓库失败: {e}[/red]")
            return 1

    if not manager.repositories:
        console.print("[yellow]没有找到仓库。请检查用户名或Token配置。[/yellow]")
        return 1

    # 计算健康评分和标签
    health_engine = HealthEngine(config)
    tag_engine = TagEngine(config)
    health_engine.score_all(manager.repositories)
    tag_engine.tag_all(manager.repositories)

    # 渲染仪表盘
    dashboard.render_dashboard(manager.repositories)
    return 0


def _cmd_list(args: argparse.Namespace, config: Config) -> int:
    """处理list子命令。

    Handle list subcommand.
    """
    dashboard = Dashboard(config=config)
    console = dashboard.console

    with dashboard.show_loading("正在加载仓库列表..."):
        manager = RepositoryManager(config=config)
        try:
            repos = manager.load_user_repos(
                username=args.user,
                sort=args.sort,
            )
        except APIError as e:
            console.print(f"[red]加载仓库失败: {e}[/red]")
            return 1

    if not repos:
        console.print("[yellow]没有找到仓库。[/yellow]")
        return 1

    # 导出功能
    if args.export:
        filepath = args.export
        if filepath.endswith(".csv"):
            manager.export_csv(filepath)
        else:
            manager.export_json(filepath)
        dashboard.print_success(f"已导出到 {filepath}")
        return 0

    # 渲染表格
    dashboard.render_repo_table(
        repos,
        show_health=False,
        show_tags=False,
        max_rows=args.limit,
    )
    return 0


def _cmd_health(args: argparse.Namespace, config: Config) -> int:
    """处理health子命令。

    Handle health subcommand.
    """
    dashboard = Dashboard(config=config)
    console = dashboard.console
    health_engine = HealthEngine(config)

    # 指定单个仓库
    if args.repo:
        api = GitHubAPI(config)
        try:
            owner, name = args.repo.split("/", 1)
            data = api.get_repo(owner, name)
            from .core import Repository
            repo = Repository.from_github_api(data)
            # 丰富信息
            manager = RepositoryManager(config=config, api=api)
            manager.enrich_repository(repo)
            report = health_engine.score(repo)
            dashboard.render_health_report([report], detailed=True)
        except (ValueError, APIError) as e:
            console.print(f"[red]获取仓库失败: {e}[/red]")
            return 1
        return 0

    # 批量评分
    with dashboard.show_loading("正在加载仓库数据..."):
        manager = RepositoryManager(config=config)
        try:
            repos = manager.load_user_repos(username=args.user)
        except APIError as e:
            console.print(f"[red]加载仓库失败: {e}[/red]")
            return 1

    if not repos:
        console.print("[yellow]没有找到仓库。[/yellow]")
        return 1

    reports = health_engine.score_all(repos)
    dashboard.render_health_report(reports, detailed=args.detailed)
    return 0


def _cmd_search(args: argparse.Namespace, config: Config) -> int:
    """处理search子命令。

    Handle search subcommand.
    """
    dashboard = Dashboard(config=config)
    console = dashboard.console
    search_filter = SearchFilter(config)

    if args.github:
        # 使用GitHub API搜索
        try:
            repos = search_filter.search_github(
                query=args.query,
                language=args.language,
                min_stars=args.min_stars,
            )
            dashboard.render_search_results(repos, args.query)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            return 1
    else:
        # 本地过滤
        if not args.user:
            console.print(
                "[yellow]本地过滤需要指定 --user 参数加载仓库数据。[/yellow]"
            )
            console.print(
                "[yellow]或者使用 --github 参数通过GitHub API搜索。[/yellow]"
            )
            return 1

        with dashboard.show_loading("正在加载仓库数据..."):
            manager = RepositoryManager(config=config)
            try:
                repos = manager.load_user_repos(username=args.user)
            except APIError as e:
                console.print(f"[red]加载仓库失败: {e}[/red]")
                return 1

        # 先打标签（用于标签过滤）
        tag_engine = TagEngine(config)
        tag_engine.tag_all(repos)

        filtered = search_filter.filter_repos(
            repos,
            language=args.language,
            min_stars=args.min_stars,
            max_stars=args.max_stars,
            min_forks=args.min_forks,
            updated_within_days=args.updated_within,
            keyword=args.query if args.query else None,
            sort_by=args.sort_by,
        )

        dashboard.render_search_results(filtered, args.query or "所有仓库")

    return 0


def _cmd_tags(args: argparse.Namespace, config: Config) -> int:
    """处理tags子命令。

    Handle tags subcommand.
    """
    dashboard = Dashboard(config=config)
    console = dashboard.console
    tag_engine = TagEngine(config)

    # 列出所有标签定义
    if args.list_all:
        all_tags = tag_engine.list_all_tags()
        from rich.table import Table
        from rich import box

        table = Table(
            title="所有可用标签",
            box=box.ROUNDED,
        )
        table.add_column("标签", style="cyan", min_width=20)
        table.add_column("描述", min_width=40)

        for tag, desc in all_tags.items():
            table.add_row(tag, desc)

        console.print(table)
        return 0

    # 为仓库生成标签
    with dashboard.show_loading("正在分析仓库标签..."):
        manager = RepositoryManager(config=config)
        try:
            repos = manager.load_user_repos(username=args.user)
        except APIError as e:
            console.print(f"[red]加载仓库失败: {e}[/red]")
            return 1

    if not repos:
        console.print("[yellow]没有找到仓库。[/yellow]")
        return 1

    tag_stats = tag_engine.get_tag_stats(repos)
    dashboard.render_tag_report(tag_stats)
    return 0


def _cmd_batch(args: argparse.Namespace, config: Config) -> int:
    """处理batch子命令。

    Handle batch subcommand.
    """
    dashboard = Dashboard(config=config)
    console = dashboard.console

    # 加载仓库
    with dashboard.show_loading("正在加载仓库数据..."):
        manager = RepositoryManager(config=config)
        try:
            repos = manager.load_user_repos(username=args.user)
        except APIError as e:
            console.print(f"[red]加载仓库失败: {e}[/red]")
            return 1

    if not repos:
        console.print("[yellow]没有找到仓库。[/yellow]")
        return 1

    # 先打标签
    tag_engine = TagEngine(config)
    tag_engine.tag_all(repos)

    batch_op = BatchOperator(config=config)

    # 确定操作目标
    target_repos = repos
    if args.repos:
        target_repos = batch_op.filter_by_names(repos, args.repos)
        if not target_repos:
            console.print("[red]未找到指定的仓库。[/red]")
            return 1
    elif args.filter_tag:
        target_repos = [r for r in repos if args.filter_tag in r.tags]
        if not target_repos:
            console.print(
                f"[yellow]没有标签为 '{args.filter_tag}' 的仓库。[/yellow]"
            )
            return 1

    if args.action == "star":
        console.print(
            f"[blue]准备Star {len(target_repos)} 个仓库...[/blue]"
        )
        result = batch_op.batch_star(target_repos)
        console.print(
            f"[green]成功: {len(result['success'])} 个[/green]"
        )
        if result["failed"]:
            console.print(f"[red]失败: {len(result['failed'])} 个[/red]")
            for fail in result["failed"]:
                console.print(f"  [red]- {fail['repo']}: {fail['reason']}[/red]")

    elif args.action == "unstar":
        console.print(
            f"[blue]准备取消Star {len(target_repos)} 个仓库...[/blue]"
        )
        result = batch_op.batch_unstar(target_repos)
        console.print(
            f"[green]成功: {len(result['success'])} 个[/green]"
        )
        if result["failed"]:
            console.print(f"[red]失败: {len(result['failed'])} 个[/red]")

    elif args.action == "export":
        if not args.output:
            console.print("[red]export操作需要指定 --output 参数。[/red]")
            return 1

        filepath = args.output
        if args.format == "csv":
            batch_op.batch_export_csv(target_repos, filepath)
        else:
            batch_op.batch_export_json(target_repos, filepath)
        dashboard.print_success(
            f"已导出 {len(target_repos)} 个仓库到 {filepath}"
        )

    return 0


def _cmd_deps(args: argparse.Namespace, config: Config) -> int:
    """处理deps子命令。

    Handle deps subcommand.
    """
    dashboard = Dashboard(config=config)
    console = dashboard.console
    checker = DependencyChecker()

    # 显示漏洞数据库信息
    if args.db_info:
        info = checker.get_vulnerability_db_info()
        from rich.table import Table
        from rich import box

        console.print(
            f"[bold]漏洞数据库信息[/bold]\n"
            f"  追踪包数: {info['total_packages_tracked']}\n"
            f"  漏洞总数: {info['total_vulnerabilities']}\n"
            f"  严重程度分布: {info['severity_distribution']}\n"
        )
        return 0

    # 检查依赖文件
    if not args.file:
        console.print("[red]请指定依赖文件路径。[/red]")
        console.print("[yellow]用法: repopulse deps <requirements.txt|package.json>[/yellow]")
        return 1

    result = checker.check_file(args.file)
    dashboard.render_deps_report(result)
    return 0


def _cmd_config(args: argparse.Namespace, config: Config) -> int:
    """处理config子命令。

    Handle config subcommand.
    """
    console = Dashboard(config=config).console

    if args.action == "show":
        from rich.table import Table
        from rich import box

        table = Table(
            title="RepoPulse 配置",
            box=box.ROUNDED,
        )
        table.add_column("配置项", style="cyan", min_width=25)
        table.add_column("值", min_width=40)

        # 显示配置（隐藏Token的中间部分）
        token = config.github_token
        if token:
            masked = token[:6] + "..." + token[-4:] if len(token) > 10 else "***"
        else:
            masked = "(未设置)"

        table.add_row("GitHub Token", masked)
        table.add_row("默认用户", config.default_user or "(未设置)")
        table.add_row("缓存有效期", f"{config.cache_ttl} 秒")
        table.add_row("API基础URL", config.api_base_url)
        table.add_row("每页数量", str(config.per_page))
        table.add_row("配置文件路径", str(config._config_path))

        console.print(table)
        console.print(
            "\n[dim]提示: 使用环境变量 GITHUB_TOKEN 或 REPOPULSE_DEFAULT_USER "
            "可以覆盖配置文件设置。[/dim]"
        )

    elif args.action == "set-token":
        if not args.value:
            console.print("[red]请提供Token值。[/red]")
            return 1
        config.set("github_token", args.value)
        config.save()
        console.print("[green]GitHub Token已保存。[/green]")

    elif args.action == "set-user":
        if not args.value:
            console.print("[red]请提供用户名。[/red]")
            return 1
        config.set("default_user", args.value)
        config.save()
        console.print(f"[green]默认用户已设置为 '{args.value}'。[/green]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
