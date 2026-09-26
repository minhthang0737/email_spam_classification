"""Seed 300+ deterministic synthetic training emails for repeatable demos."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app import create_app, db
from app.models.email_dataset import EmailDataset

SAMPLE_DATA = [
    ("Congratulations! You won $5000. Click here to claim.", "SPAM"),
    ("You have won a free prize. Claim your reward now.", "SPAM"),
    ("Free money waiting for you. Act now!", "SPAM"),
    ("Winner! Your lottery prize is ready.", "SPAM"),
    ("Limited offer: earn cash instantly.", "SPAM"),
    ("Meeting at 10 AM tomorrow in room 201.", "NOT_SPAM"),
    ("Please review the project document before Friday.", "NOT_SPAM"),
    ("Can we schedule a meeting tomorrow afternoon?", "NOT_SPAM"),
    ("The team lunch is at 12 PM today.", "NOT_SPAM"),
    ("Reminder: submit your assignment by Sunday.", "NOT_SPAM"),
    ("Your account statement is available online.", "NOT_SPAM"),
    ("Project update: sprint review on Thursday.", "NOT_SPAM"),
    ("Chúc mừng! Bạn đã trúng thưởng điện thoại miễn phí. Nhấn liên kết để nhận quà ngay hôm nay.", "SPAM"),
    ("Cơ hội kiếm tiền nhanh tại nhà. Đăng ký ngay để nhận khoản thưởng lớn.", "SPAM"),
    ("Tài khoản của bạn sẽ bị khóa. Cập nhật mật khẩu tại đường dẫn này ngay lập tức.", "SPAM"),
    ("Chào nhóm, cuộc họp dự án bắt đầu lúc 10 giờ sáng thứ Năm tại phòng 201.", "NOT_SPAM"),
    ("Nhờ bạn gửi bản báo cáo trước 5 giờ chiều thứ Sáu để mình tổng hợp.", "NOT_SPAM"),
    ("Nhóm mình ăn trưa lúc 12 giờ ở căn tin trường hôm nay nhé.", "NOT_SPAM"),
]


def make_bulk_samples():
    spam_subjects = [
        "URGENT account alert", "Exclusive cash offer", "Prize claim notice",
        "Verify your account now", "Limited-time reward", "Unpaid parcel fee",
        "Work from home income", "Lottery winner notification", "Security warning",
        "Khuyến mãi đặc biệt", "Thông báo trúng thưởng", "Xác minh tài khoản",
        "Cơ hội nhận quà", "Ưu đãi dành riêng", "Cảnh báo thanh toán",
    ]
    spam_bodies = [
        "Click the link to claim your reward immediately.",
        "Send your password and card number to release the payment.",
        "You were selected for a cash prize; respond before it expires.",
        "Pay a small delivery charge to receive your free gift.",
        "Confirm your bank details today or your account will be closed.",
        "Earn guaranteed income with no experience and an upfront fee.",
        "Your parcel is on hold. Open the attached link to pay now.",
        "Chọn liên kết để nhận quà miễn phí ngay hôm nay.",
        "Tài khoản sẽ bị khóa nếu bạn không xác minh mật khẩu.",
        "Chuyển phí xử lý để giải ngân khoản thưởng lớn.",
        "Đăng ký ngay để kiếm tiền nhanh, cam kết lợi nhuận.",
        "Thông tin ngân hàng cần được cập nhật qua biểu mẫu này.",
        "Nhận phiếu mua hàng giá trị cao, số lượng có hạn.",
        "Bạn đã trúng giải, hãy trả lời kèm thông tin cá nhân.",
        "Thanh toán khoản phí nhỏ để mở khóa phần quà.",
        "Your confidential offer is waiting; act now and do not delay.",
        "We need your one-time code to prevent service interruption.",
        "Get a guaranteed refund after you submit the registration fee.",
        "Bấm vào đây để nhận ưu đãi trước khi chương trình kết thúc.",
        "Vui lòng cung cấp mã OTP để tránh gián đoạn dịch vụ.",
    ]
    safe_subjects = [
        "Meeting schedule", "Project status update", "Course reminder",
        "Team lunch this week", "Invoice for review", "Document feedback",
        "Weekly planning notes", "Library opening hours", "Lịch họp tuần này",
        "Nhắc nộp báo cáo", "Cập nhật đồ án", "Biên bản cuộc họp",
        "Thông báo lịch học", "Kế hoạch làm việc", "Tài liệu cần góp ý",
    ]
    safe_bodies = [
        "Please review the attached agenda before our regular team meeting.",
        "The project draft is ready; add comments by Friday afternoon.",
        "Our appointment is confirmed for 10 AM in room 204.",
        "I shared the lecture notes in the course workspace.",
        "Could you approve the invoice through the usual finance system?",
        "The team lunch is at noon; let me know if you can attend.",
        "Please send the weekly report to the project folder.",
        "Thanks for helping with the presentation and lab review.",
        "Nhờ bạn xem bản dự thảo trước buổi họp chiều thứ Sáu.",
        "Cuộc họp nhóm bắt đầu lúc 9 giờ tại phòng thực hành.",
        "Mình đã gửi tài liệu môn học lên thư mục chung của lớp.",
        "Bạn vui lòng phản hồi hóa đơn qua hệ thống kế toán quen thuộc.",
        "Nhóm sẽ ăn trưa lúc 12 giờ, bạn tham gia nhé.",
        "Bản báo cáo tuần đã được lưu trong thư mục dự án.",
        "Cảm ơn bạn đã góp ý cho phần trình bày hôm qua.",
        "The library will close at 8 PM during the examination week.",
        "Can we move the code review to Thursday morning?",
        "Please find the updated class timetable attached.",
        "Tài liệu họp đã được cập nhật, mọi người góp ý trước thứ Hai.",
        "Mình xác nhận sẽ tham gia buổi trao đổi về đồ án.",
    ]
    samples = []
    for label, subjects, bodies in (
        ("SPAM", spam_subjects, spam_bodies),
        ("NOT_SPAM", safe_subjects, safe_bodies),
    ):
        for i in range(150):
            subject = subjects[i % len(subjects)]
            body = bodies[(i * 7 + i // len(subjects)) % len(bodies)]
            samples.append((f"Subject: {subject} [{i + 1:03d}]\n\n{body}", label))
    return samples

app = create_app()

with app.app_context():
    known = {row.email_content for row in EmailDataset.query.with_entities(EmailDataset.email_content)}
    samples = SAMPLE_DATA + make_bulk_samples()
    added = 0
    for email_content, label in samples:
        if email_content not in known:
            db.session.add(EmailDataset(email_content=email_content, label=label))
            known.add(email_content)
            added += 1
    db.session.commit()
    print(f"Added {added} unique training emails; dataset now has {len(known)} records.")
