"""
농지알리미 이메일 발송 테스트 스크립트
.env에서 GMAIL_USER, GMAIL_APP_PASSWORD, ALERT_FROM_NAME을 읽어
Gmail SMTP로 테스트 이메일을 발송합니다.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv
import os

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
ALERT_FROM_NAME = os.getenv("ALERT_FROM_NAME", "알리미")


def build_html():
    return """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
</head>
<body style="margin:0; padding:0; background-color:#f5f5f0; font-family:'Apple SD Gothic Neo','Malgun Gothic',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f5f5f0; padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="background-color:#ffffff; border-radius:16px; overflow:hidden; box-shadow:0 2px 12px rgba(0,0,0,0.08);">

          <!-- 헤더 -->
          <tr>
            <td style="background: linear-gradient(135deg, #2d6a4f, #40916c); padding:32px 40px; text-align:center;">
              <div style="font-size:36px; margin-bottom:8px;">🌾</div>
              <h1 style="margin:0; color:#ffffff; font-size:22px; font-weight:700;">
                농지알리미
              </h1>
              <p style="margin:6px 0 0; color:#b7e4c7; font-size:14px;">
                새로운 매물이 도착했습니다
              </p>
            </td>
          </tr>

          <!-- 본문 -->
          <tr>
            <td style="padding:36px 40px;">
              <p style="margin:0 0 24px; color:#333333; font-size:16px; line-height:1.6;">
                안녕하세요! 😊<br/>
                설정하신 조건에 맞는 <strong>새 매물</strong>을 찾았어요.
              </p>

              <!-- 매물 카드 -->
              <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#f8faf8; border:1px solid #d8f3dc; border-radius:12px; overflow:hidden; margin-bottom:28px;">
                <tr>
                  <td style="padding:24px;">
                    <table width="100%" cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="padding-bottom:12px; border-bottom:1px dashed #b7e4c7;">
                          <span style="display:inline-block; background-color:#2d6a4f; color:#ffffff; font-size:11px; font-weight:700; padding:4px 10px; border-radius:20px; margin-bottom:8px;">
                            임대 · 답
                          </span>
                          <h2 style="margin:8px 0 0; color:#1b4332; font-size:18px; font-weight:700;">
                            전남 나주시 나포면
                          </h2>
                        </td>
                      </tr>
                      <tr>
                        <td style="padding-top:16px;">
                          <table width="100%" cellpadding="0" cellspacing="0">
                            <tr>
                              <td width="50%" style="padding:6px 0;">
                                <span style="color:#6c757d; font-size:12px;">면적</span><br/>
                                <span style="color:#333333; font-size:15px; font-weight:600;">820㎡ (248평)</span>
                              </td>
                              <td width="50%" style="padding:6px 0;">
                                <span style="color:#6c757d; font-size:12px;">임대료</span><br/>
                                <span style="color:#2d6a4f; font-size:15px; font-weight:600;">연 42만원</span>
                              </td>
                            </tr>
                            <tr>
                              <td width="50%" style="padding:6px 0;">
                                <span style="color:#6c757d; font-size:12px;">지목</span><br/>
                                <span style="color:#333333; font-size:15px; font-weight:600;">답 (논)</span>
                              </td>
                              <td width="50%" style="padding:6px 0;">
                                <span style="color:#6c757d; font-size:12px;">평당가</span><br/>
                                <span style="color:#333333; font-size:15px; font-weight:600;">약 1,694원/평</span>
                              </td>
                            </tr>
                          </table>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <!-- CTA 버튼 -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center">
                    <a href="https://www.fbo.or.kr" target="_blank"
                       style="display:inline-block; background-color:#2d6a4f; color:#ffffff; text-decoration:none; font-size:15px; font-weight:700; padding:14px 36px; border-radius:8px;">
                      🏡 농지은행 바로가기
                    </a>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- 푸터 -->
          <tr>
            <td style="background-color:#f8faf8; padding:24px 40px; text-align:center; border-top:1px solid #e9ecef;">
              <p style="margin:0 0 4px; color:#999999; font-size:12px;">
                본 메일은 농지알리미 테스트 발송입니다.
              </p>
              <p style="margin:0; color:#bbbbbb; font-size:11px;">
                © 2026 농지알리미 · 이 메일은 자동 발송되었습니다.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def send_test_email(to_email: str):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "알리미가 새 매물을 찾았어요! 🌾"
    msg["From"] = formataddr((ALERT_FROM_NAME, GMAIL_USER))
    msg["To"] = to_email

    msg.attach(MIMEText(build_html(), "html", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())

    print(f"✅ 이메일 발송 완료 → {to_email}")


if __name__ == "__main__":
    recipient = input("수신 이메일 주소를 입력하세요: ").strip()
    if not recipient:
        print("❌ 이메일 주소가 입력되지 않았습니다.")
    else:
        send_test_email(recipient)
