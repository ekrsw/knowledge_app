"""
Factory smoke tests - 手動検証用の簡単なテスト
各ファクトリーが基本的に動作することを確認
"""
import pytest
from tests.factories import (
    UserFactory,
    ApprovalGroupFactory,
    InfoCategoryFactory,
    ArticleFactory,
    RevisionFactory,
    NotificationFactory
)


@pytest.mark.asyncio
async def test_all_factories_basic_smoke(db_session):
    """全ファクトリーの基本動作確認（スモークテスト）"""
    
    # 1. ApprovalGroup
    approval_group = await ApprovalGroupFactory.create_development_group(db_session)
    assert approval_group.group_name == "Development Team"
    print(f"[OK] ApprovalGroupFactory: {approval_group.group_name}")
    
    # 2. InfoCategory  
    info_category = await InfoCategoryFactory.create_technology_category(db_session)
    assert info_category.category_name == "Technology"
    print(f"[OK] InfoCategoryFactory: {info_category.category_name}")
    
    # 3. User (各ロール)
    admin_user = await UserFactory.create_admin(db_session)
    approver_user = await UserFactory.create_approver(db_session, approval_group)
    regular_user = await UserFactory.create_user(db_session)
    
    assert admin_user.role == "admin"
    assert approver_user.role == "approver"
    assert regular_user.role == "user"
    print(f"[OK] UserFactory: admin, approver, user roles created")
    
    # 4. Article
    article = await ArticleFactory.create(
        db_session,
        info_category=info_category,
        approval_group=approval_group
    )
    assert article.info_category == info_category.category_id
    assert article.approval_group == approval_group.group_id
    print(f"[OK] ArticleFactory: {article.title}")
    
    # 5. Revision (各ステータス)
    draft_revision = await RevisionFactory.create_draft(
        db_session,
        proposer=regular_user,
        approver=approver_user
    )
    assert draft_revision.status == "draft"
    assert draft_revision.proposer_id == regular_user.id
    assert draft_revision.approver_id == approver_user.id
    print(f"[OK] RevisionFactory: {draft_revision.status} revision created")
    
    # 6. Notification
    notification = await NotificationFactory.create_revision_submitted(
        db_session,
        approver=approver_user,
        revision=draft_revision
    )
    assert notification.type == "revision_submitted"
    assert notification.user_id == approver_user.id
    assert notification.revision_id == draft_revision.revision_id
    print(f"[OK] NotificationFactory: {notification.type} notification created")
    
    print("\n[SUCCESS] 全6種類のファクトリーが正常動作しています！")


@pytest.mark.asyncio
async def test_factory_batch_creation(db_session):
    """ファクトリーの一括作成機能テスト"""
    
    # 一括ユーザー作成
    users = await UserFactory.create_batch(db_session, count=5, role="user")
    assert len(users) == 5
    for user in users:
        assert user.role == "user"
        assert user.id is not None
    print(f"[OK] 一括ユーザー作成: {len(users)}件")
    
    # 一括修正案作成  
    revisions = await RevisionFactory.create_batch(
        db_session, 
        count=3,
        status="draft"
    )
    assert len(revisions) == 3
    for revision in revisions:
        assert revision.status == "draft"
        assert revision.revision_id is not None
    print(f"[OK] 一括修正案作成: {len(revisions)}件")
    
    # 一括通知作成
    notifications = await NotificationFactory.create_batch(
        db_session,
        count=4,
        type="info"
    )
    assert len(notifications) == 4
    for notification in notifications:
        assert notification.type == "info"
        assert notification.id is not None
    print(f"[OK] 一括通知作成: {len(notifications)}件")
    
    print(f"\n[SUCCESS] 一括作成機能が正常動作しています！（合計{5+3+4}件作成）")


@pytest.mark.asyncio  
async def test_factory_with_content_verification(db_session):
    """ファクトリーのコンテンツ機能検証"""
    
    # コンテンツ付き修正案
    content_revision = await RevisionFactory.create_with_content(db_session)
    
    assert content_revision.after_title is not None
    assert content_revision.after_keywords is not None
    assert content_revision.after_importance is True
    assert content_revision.after_question is not None
    assert content_revision.after_answer is not None
    print("[OK] RevisionFactory: コンテンツ付き修正案作成成功")
    
    # 混合通知（既読/未読）
    user = await UserFactory.create_user(db_session)
    mixed_notifications = await NotificationFactory.create_read_and_unread_mix(
        db_session,
        user=user,
        read_count=2,
        unread_count=3
    )
    
    assert len(mixed_notifications["read"]) == 2
    assert len(mixed_notifications["unread"]) == 3
    for notif in mixed_notifications["read"]:
        assert notif.is_read is True
    for notif in mixed_notifications["unread"]:
        assert notif.is_read is False
    print("[OK] NotificationFactory: 既読/未読混合通知作成成功")
    
    print("\n[SUCCESS] コンテンツ機能が正常動作しています！")


@pytest.mark.asyncio
async def test_factory_relationship_verification(db_session):
    """ファクトリーの関係性検証"""
    
    # 関係性を持つエンティティ作成
    approval_group = await ApprovalGroupFactory.create_development_group(db_session)
    info_category = await InfoCategoryFactory.create_business_category(db_session)
    
    # ユーザー（承認グループ所属）
    approver = await UserFactory.create_approver(
        db_session,
        approval_group=approval_group
    )
    assert approver.approval_group_id == approval_group.group_id
    print("[OK] User-ApprovalGroup関係性確認")
    
    # 記事（カテゴリ・グループ関連）
    article = await ArticleFactory.create(
        db_session,
        info_category=info_category,
        approval_group=approval_group
    )
    assert article.info_category == info_category.category_id
    assert article.approval_group == approval_group.group_id
    print("[OK] Article-InfoCategory-ApprovalGroup関係性確認")
    
    # 修正案（ユーザー関連）
    proposer = await UserFactory.create_user(db_session)
    revision = await RevisionFactory.create(
        db_session,
        proposer=proposer,
        approver=approver,
        target_article_id=article.article_id
    )
    assert revision.proposer_id == proposer.id
    assert revision.approver_id == approver.id
    assert revision.target_article_id == article.article_id
    print("[OK] Revision-User-Article関係性確認")
    
    # 通知（ユーザー・修正案関連）
    notification = await NotificationFactory.create_revision_approved(
        db_session,
        proposer=proposer,
        revision=revision
    )
    assert notification.user_id == proposer.id
    assert notification.revision_id == revision.revision_id
    print("[OK] Notification-User-Revision関係性確認")
    
    print("\n[SUCCESS] 全エンティティ間関係性が正常動作しています！")


if __name__ == "__main__":
    print("手動実行には pytest を使用してください:")
    print("uv run pytest backend/tests/test_factory_smoke.py -v -s")