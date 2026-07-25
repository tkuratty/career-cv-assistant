---
slug: example-r1
opportunity: example              # opportunities/example.md に対応
company: example                  # companies/example/ に対応
round: 1
round_type: first                 # casual / first / technical / manager / executive / hr / reference / offer
format: オンライン                # 対面 / オンライン / 電話
date: 2026-02-10
duration: 60分
status: 予定                      # 予定 / 完了 / 見送り / キャンセル
cv: cv/output/example/            # 提出した CV（深掘りの中心になる）
interviewers:
  - name: サンプル 一郎（架空）
    title: IT Manager
    role_in_process: 配属先の上長（一次面接官・実質の採用決定者）
    focus: 少人数体制での優先順位付けと、日常運用をどう回すか
    sources:
      - https://example.com/company/team          # 会社サイトのチーム紹介（公開情報）
      - https://example.com/tech-blog/it-ops      # 本人の技術ブログ（公開情報）
  - name: （要確認）
    title: 人事担当
    role_in_process: 同席（転職理由・条件面の確認）
    focus: 転職理由の一貫性、入社時期
    sources: []
updated: 2026-01-01
---

# 一次面接（コーポレートIT / 株式会社サンプルテック）

> これは `prep-interview` スキルが生成する面接ファイルの**書式サンプル**です（架空）。
> 案件は [[opportunities/example]]、企業調査は [[companies/example/research]]。
> 事前ブリーフ: `python scripts/interview_brief.py --opportunity example --round 1`

## この面接の目的（相手側）
- 相手がこのラウンドで確かめたいことを 2〜3 行で。JD の要件に対する**即戦力性**の確認か、
  カルチャー適合か、レベリングか。分からなければ推測で埋めず、エージェント／採用担当に聞く。
- （見本）「JD の運用範囲を一人で回せるか」「少人数体制で優先順位を自分で決められるか」。

## 想定される評価軸
- `.claude/skills/prep-interview/references/interview-playbooks.md` の
  企業タイプ × ラウンド種別から具体化する（**一般論なので実際の進め方は要確認**）。
- （見本）日常運用の具体性 / トラブル時の判断 / セキュリティ運用の実務レベル / 自走できるか。

## 面接官メモ（公開情報のみ）
- 役割と関心領域だけを、出典つきで。私生活・私的 SNS・センシティブ属性は**調べない・書かない**。
- 同定に自信が無ければ「要確認」のままにする。推測は「推測」と明記。
- （見本）技術ブログで「運用の属人化解消」を繰り返し書いている → 仕組み化の話が刺さる可能性（推測）。

## 語り口（企業メッセージ）
- `companies/example/messages.yaml` の strength が上限。
  strong = 実績として断定 / partial = 限定詞つき / none = **主張せず逆質問へ**。
- （見本）
  - strong「現場の手作業をなくす」→ 申請フローの自動化を主エピソードに。
  - partial「ISMS 認証取得」→「認証取得の主導経験ではなく、枠組みに沿った日常運用の経験」と先に範囲を明示。
  - none「AI 前提の業務設計」→ 主張しない。逆質問（承認経路・データ分類）に回す。

## 想定質問と回答骨子
- 質問ごとに **事実 → 行動 → 結果** の順で骨子だけ。`data/career.*.yaml` の記述を超えない。
  評価語（主導・全社・大幅）を足さない。
- （見本）「一人で運用を回した経験は？」
  - 事実: 情シス機能をハンズオンで所管（[[data/career]] `ex-helpdesk`）
  - 行動: 問い合わせを Issue ベースのキューに再構築し、キッティング／オンボーディングを標準化
  - 結果: 対応状況が可視化され、属人化が減った（数値は data にある範囲で）

## 逆質問（優先順）
1. 裏付けの無い企業メッセージから（`interview_probe`）。
2. 案件の懸念・確認チェックリストの未確認項目から。
3. 入社後 90 日で期待される成果（相手の期待値を引き出す質問）。

## 直前チェック
- [ ] 提出した CV（`cv/output/example/`）を読み返した
- [ ] 接続・入室方法・所要時間・遅刻時の連絡先を確認した
- [ ] 逆質問を 3 つ以上用意した
- [ ] 話す順番（結論 → 具体 → 学び）を 1 度声に出した

## 振り返り（実施後に記入）
- 実際に聞かれたこと / 手応え / 相手の反応
- 次ラウンドへの申し送り（深掘りされた点、答えに詰まった点）
- `opportunities/example.md` の `status` と選考ログを更新する
