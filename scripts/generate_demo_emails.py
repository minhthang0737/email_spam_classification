"""Generate a reproducible, balanced 100,000-row synthetic email seed CSV."""

import argparse
import csv
import gzip
import random
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "demo_emails_100k.csv.gz"

SPAM_DOMAINS = ["claim-prize.test", "secure-wallet.test", "parcel-alert.test", "bonus-reward.test", "xacminh-taikhoan.test"]
SAFE_DOMAINS = ["uit.edu.vn", "team.example.org", "library.example.net", "company.example.com", "classroom.example.org"]
SPAM_SUBJECTS = [
    "[Cảnh báo] Xác minh tài khoản ngay", "Bạn nhận được phần thưởng đặc biệt",
    "URGENT: payment needs confirmation", "Gói hàng đang chờ thanh toán phí",
    "Cơ hội nhận quà chỉ dành cho bạn", "Your refund is ready to claim",
    "Tài khoản có nguy cơ bị khóa", "Exclusive investment return offer",
    "Mã ưu đãi sắp hết hạn", "Unusual activity detected - verify now",
]
SAFE_SUBJECTS = [
    "Lịch học tuần này", "Biên bản họp nhóm đồ án", "Project review notes",
    "Tài liệu môn học đã cập nhật", "Invoice for your review", "Meeting moved to Thursday",
    "Nhắc lịch nộp báo cáo", "Library opening hours", "Weekly status update",
    "Xác nhận lịch hẹn với nhóm",
]
SPAM_BODIES = [
    "Nhấn liên kết để nhận quà ngay: https://claim-prize.test/offer/{code}. Không chia sẻ thông tin này.",
    "Vui lòng gửi mã OTP và mật khẩu để xác nhận giao dịch. Truy cập http://secure-wallet.test/verify/{code}.",
    "Thanh toán khoản phí nhỏ trong hôm nay để mở khóa phần thưởng của bạn.",
    "You were selected for a cash reward. Reply with your card details before the offer expires.",
    "Tài khoản sẽ bị tạm khóa. Cập nhật thông tin ngân hàng tại https://xacminh-taikhoan.test/login/{code}.",
    "Guaranteed income with no experience. Pay the registration fee and start today.",
    "Đơn hàng bị giữ lại. Bấm vào đường dẫn lạ để thanh toán phí giao hàng ngay.",
    "Your one-time code is required to prevent service interruption. Send it to us now.",
]
SAFE_BODIES = [
    "Mình gửi biên bản cuộc họp để mọi người góp ý trước thứ Sáu.",
    "Please review the attached project notes before our regular team meeting.",
    "Tài liệu bài giảng đã được tải lên thư mục chung của lớp.",
    "Can we move the code review to Thursday morning? The calendar invite is updated.",
    "Hóa đơn đã được gửi qua cổng thanh toán quen thuộc để bạn kiểm tra.",
    "The library will close at 8 PM during examination week. No action is needed.",
    "Nhóm xác nhận lịch hẹn lúc 9 giờ tại phòng thực hành như đã thống nhất.",
    "Thanks for the weekly report. I added comments to the shared project document.",
]
FIRST_NAMES = ["minh", "linh", "an", "hoa", "tuan", "ngoc", "phuc", "mai", "alex", "jordan"]


def generate_rows(count=100_000, seed=20260926):
    rng = random.Random(seed)
    for index in range(count):
        label = "SPAM" if index % 2 == 0 else "NOT_SPAM"
        spam = label == "SPAM"
        domain = rng.choice(SPAM_DOMAINS if spam else SAFE_DOMAINS)
        sender = f"{rng.choice(FIRST_NAMES)}{index:06d}@{domain}"
        recipient = f"student{index % 5000:04d}@uit.edu.vn"
        subject = rng.choice(SPAM_SUBJECTS if spam else SAFE_SUBJECTS)
        body = rng.choice(SPAM_BODIES if spam else SAFE_BODIES).format(code=f"{index:06d}")
        # Every row has reproducible metadata and unique content for clean re-import.
        content = (
            f"From: {sender}\nTo: {recipient}\nSubject: {subject} [{index + 1:06d}]\n"
            f"Message-ID: <demo-{index + 1:06d}@seed.local>\n\n{body}"
        )
        yield content, label


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=100_000)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if args.count < 1:
        parser.error("--count must be positive")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(args.output, "wt", encoding="utf-8", newline="", compresslevel=6) as stream:
        writer = csv.writer(stream)
        writer.writerow(["email", "label"])
        writer.writerows(generate_rows(args.count))
    print(f"Generated {args.count:,} synthetic emails at {args.output}")


if __name__ == "__main__":
    main()
