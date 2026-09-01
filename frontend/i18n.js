"use strict";

const translations = {
  en: {
    "欢迎回来": "Welcome back", "登录你的工作台": "Sign in to your workspace",
    "继续推进那些真正重要的事情。": "Keep moving what truly matters forward.",
    "创建一个新账户": "Create a new account", "从一个清晰的计划开始。": "Start with a clear plan.",
    "登录": "Sign in", "创建账户": "Create account", "邮箱": "Email", "密码": "Password",
    "用户名": "Username", "进入工作台": "Open workspace", "任务概览": "Overview",
    "标签管理": "Labels", "账户设置": "Settings", "管理中心": "Admin",
    "刷新": "Refresh", "新建任务": "New task", "你好，": "Hello, ", "朋友": "Friend",
    "把注意力放在下一步，而不是所有步骤。": "Focus on the next step, not every step.",
    "完成率": "Completion", "任务总数": "Total tasks", "符合当前筛选条件": "Matching current filters",
    "待处理": "Pending", "当前页任务": "Tasks on this page", "进行中": "In progress",
    "正在推进": "Moving forward", "已完成": "Completed", "当前页成果": "Completed on this page",
    "任务列表": "Task list", "全部状态": "All statuses", "全部优先级": "All priorities",
    "这里还很安静": "Nothing here yet", "创建第一个任务，让计划开始运转。": "Create your first task to get things moving.",
    "我的标签": "My labels", "还没有标签，在右侧创建一个吧。": "No labels yet. Create one on the right.",
    "创建标签": "Create label", "标签名称": "Label name", "标签颜色": "Label color",
    "关联到任务": "Assign to task", "选择任务": "Select task", "选择标签": "Select label",
    "添加": "Add", "移除": "Remove", "基本资料": "Profile", "保存资料": "Save profile",
    "修改密码": "Change password", "当前密码": "Current password", "新密码": "New password",
    "更新密码": "Update password", "界面偏好": "Appearance & language",
    "选择皮肤": "Choose theme", "选择语言": "Choose language",
    "森林青柠": "Forest Lime", "海岸蓝": "Coastal Blue", "暖阳珊瑚": "Warm Coral",
    "石墨银": "Graphite Silver", "樱花墨": "Sakura Ink",
    "用户管理": "Users", "全站任务": "All tasks", "用户列表": "User list",
    "新建任务": "New task", "编辑任务": "Edit task", "任务标题": "Task title",
    "任务描述": "Description", "优先级": "Priority", "截止时间": "Due date",
    "每天重复": "Repeat daily", "完成后自动创建下一天的任务": "Create the next day's task when completed",
    "取消": "Cancel", "保存任务": "Save task", "普通用户": "User", "管理员": "Administrator",
    "无截止时间": "No due date", "暂无描述": "No description", "每天": "Daily",
    "上一页": "Previous", "下一页": "Next", "暂无数据": "No data",
    "已启用": "Enabled", "已禁用": "Disabled", "禁用": "Disable", "启用": "Enable", "删除": "Delete",
    "P1 · 最低": "P1 · Lowest", "P2 · 较低": "P2 · Low", "P3 · 普通": "P3 · Normal",
    "P4 · 较高": "P4 · High", "P5 · 最高": "P5 · Highest",
    "登录成功，欢迎回来": "Signed in. Welcome back.", "已安全退出": "Signed out safely.",
    "任务状态已更新": "Task status updated.", "已完成，明日任务已自动创建": "Completed. Tomorrow's task was created.",
    "任务已创建": "Task created.", "任务已更新": "Task updated.", "任务已删除": "Task deleted.",
    "已开启每天重复": "Daily repeat enabled.", "已关闭每天重复": "Daily repeat disabled.",
    "标签已创建": "Label created.", "标签已添加到任务": "Label assigned to task.",
    "已从任务移除标签": "Label removed from task.", "个人资料已更新": "Profile updated.",
    "密码已更新": "Password updated.", "处理中…": "Working…", "保存中…": "Saving…",
    "请输入密码": "Enter your password", "你的名字": "Your name", "设置登录密码": "Create a password",
    "要完成什么？": "What needs to be done?", "补充一些背景或执行说明": "Add context or notes",
    "例如：后端": "For example: Backend"
  },
  ja: {
    "欢迎回来": "おかえりなさい", "登录你的工作台": "ワークスペースにログイン",
    "继续推进那些真正重要的事情。": "本当に大切なことを進めましょう。",
    "创建一个新账户": "新しいアカウントを作成", "从一个清晰的计划开始。": "明確な計画から始めましょう。",
    "登录": "ログイン", "创建账户": "アカウント作成", "邮箱": "メール", "密码": "パスワード",
    "用户名": "ユーザー名", "进入工作台": "ワークスペースへ", "任务概览": "タスク概要",
    "标签管理": "ラベル管理", "账户设置": "設定", "管理中心": "管理",
    "刷新": "更新", "新建任务": "新規タスク", "你好，": "こんにちは、", "朋友": "ゲスト",
    "把注意力放在下一步，而不是所有步骤。": "すべてではなく、次の一歩に集中しましょう。",
    "完成率": "完了率", "任务总数": "タスク総数", "符合当前筛选条件": "現在の条件に一致",
    "待处理": "未着手", "当前页任务": "このページのタスク", "进行中": "進行中",
    "正在推进": "進行中", "已完成": "完了", "当前页成果": "このページの完了数",
    "任务列表": "タスク一覧", "全部状态": "すべての状態", "全部优先级": "すべての優先度",
    "这里还很安静": "タスクはまだありません", "创建第一个任务，让计划开始运转。": "最初のタスクを作成しましょう。",
    "我的标签": "マイラベル", "还没有标签，在右侧创建一个吧。": "ラベルはまだありません。右側で作成できます。",
    "创建标签": "ラベル作成", "标签名称": "ラベル名", "标签颜色": "ラベル色",
    "关联到任务": "タスクに割り当て", "选择任务": "タスクを選択", "选择标签": "ラベルを選択",
    "添加": "追加", "移除": "解除", "基本资料": "プロフィール", "保存资料": "プロフィールを保存",
    "修改密码": "パスワード変更", "当前密码": "現在のパスワード", "新密码": "新しいパスワード",
    "更新密码": "パスワードを更新", "界面偏好": "外観と言語",
    "选择皮肤": "テーマを選択", "选择语言": "言語を選択",
    "森林青柠": "フォレストライム", "海岸蓝": "コースタルブルー", "暖阳珊瑚": "ウォームコーラル",
    "石墨银": "グラファイト", "樱花墨": "サクラ墨",
    "用户管理": "ユーザー管理", "全站任务": "全タスク", "用户列表": "ユーザー一覧",
    "编辑任务": "タスク編集", "任务标题": "タスク名", "任务描述": "説明",
    "优先级": "優先度", "截止时间": "期限", "每天重复": "毎日繰り返す",
    "完成后自动创建下一天的任务": "完了時に翌日のタスクを自動作成", "取消": "キャンセル",
    "保存任务": "タスクを保存", "普通用户": "一般ユーザー", "管理员": "管理者",
    "无截止时间": "期限なし", "暂无描述": "説明なし", "每天": "毎日",
    "上一页": "前へ", "下一页": "次へ", "暂无数据": "データなし",
    "已启用": "有効", "已禁用": "無効", "禁用": "無効化", "启用": "有効化", "删除": "削除",
    "P1 · 最低": "P1 · 最低", "P2 · 较低": "P2 · 低", "P3 · 普通": "P3 · 標準",
    "P4 · 较高": "P4 · 高", "P5 · 最高": "P5 · 最高",
    "登录成功，欢迎回来": "ログインしました。おかえりなさい。", "已安全退出": "安全にログアウトしました。",
    "任务状态已更新": "タスクの状態を更新しました。", "已完成，明日任务已自动创建": "完了しました。明日のタスクを作成しました。",
    "任务已创建": "タスクを作成しました。", "任务已更新": "タスクを更新しました。", "任务已删除": "タスクを削除しました。",
    "已开启每天重复": "毎日の繰り返しを有効にしました。", "已关闭每天重复": "毎日の繰り返しを無効にしました。",
    "标签已创建": "ラベルを作成しました。", "标签已添加到任务": "タスクにラベルを追加しました。",
    "已从任务移除标签": "タスクからラベルを外しました。", "个人资料已更新": "プロフィールを更新しました。",
    "密码已更新": "パスワードを更新しました。", "处理中…": "処理中…", "保存中…": "保存中…",
    "请输入密码": "パスワードを入力", "你的名字": "お名前", "设置登录密码": "パスワードを設定",
    "要完成什么？": "何を完了しますか？", "补充一些背景或执行说明": "背景やメモを追加",
    "例如：后端": "例：バックエンド"
  }
};

function t(source) {
  const language = localStorage.getItem("taskflow_language") || "zh";
  return translations[language]?.[source] || source;
}

function translatePage(root = document.body) {
  const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
  let node = walker.nextNode();
  while (node) {
    const text = node.textContent;
    const source = node.__i18nSource || text.trim();
    if (source && !["SCRIPT", "STYLE"].includes(node.parentElement?.tagName)) {
      node.__i18nSource = source;
      node.textContent = text.replace(text.trim(), t(source));
    }
    node = walker.nextNode();
  }
  root.querySelectorAll?.("[placeholder], [title], [aria-label]").forEach((element) => {
    ["placeholder", "title", "aria-label"].forEach((attribute) => {
      if (!element.hasAttribute(attribute)) return;
      const key = `i18n${attribute.replace("-", "").replace(/^./, (char) => char.toUpperCase())}`;
      const source = element.dataset[key] || element.getAttribute(attribute);
      element.dataset[key] = source;
      element.setAttribute(attribute, t(source));
    });
  });
}

window.TaskFlowI18n = { t, translatePage };
