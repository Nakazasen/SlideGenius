"""Generate a Vietnamese workshop deck using the SlideGenius core exporter."""
import os
import sys
from pathlib import Path

sys.path.append(os.getcwd())

from src.core.pptx_generator import PPTXGenerator, TEMPLATES
from src.data.models import Outline, SlideItem, SlideType


def build_outline() -> Outline:
    return Outline(
        title="Workshop Psychological Safety",
        slides=[
            SlideItem(
                title="Workshop Psychological Safety",
                slide_type=SlideType.TITLE,
                subtitle="Tạo môi trường an toàn để lên tiếng, học hỏi và hợp tác tốt hơn",
                key_message="Workshop 90-120 phút cho trải nghiệm, thảo luận và cam kết hành động",
            ),
            SlideItem(
                title="Mục tiêu Workshop",
                layout_variant="agenda",
                summary="Sau buổi workshop, người tham gia cần hiểu, nhận biết, trải nghiệm và hành động.",
                bullets=[
                    "Hiểu khái niệm Psychological Safety",
                    "Nhận biết dấu hiệu của môi trường thiếu an toàn tâm lý",
                    "Hiểu ảnh hưởng của hành vi cấp trên và cấp dưới",
                    "Trải nghiệm cảm giác an toàn và không an toàn",
                    "Có hành động cụ thể để cải thiện môi trường làm việc",
                ],
            ),
            SlideItem(
                title="Khung thời lượng đề xuất",
                layout_variant="stats_highlight",
                summary="Tổng thời lượng workshop: khoảng 90-120 phút.",
                stats=[
                    {"label": "Ice Break", "value": "15'", "insight": "Tạo không khí an toàn và kích hoạt tham gia"},
                    {"label": "Giới thiệu khái niệm", "value": "15'", "insight": "Định nghĩa và phân biệt đúng Psychological Safety"},
                    {"label": "Trải nghiệm + thảo luận", "value": "60-80'", "insight": "Game, thảo luận nhóm, tổng kết và cam kết"},
                ],
                key_message="Nên giữ nhịp workshop nhanh, nhiều tương tác và ưu tiên trải nghiệm trực tiếp.",
            ),
            SlideItem(
                title="Cấu trúc workshop chi tiết",
                layout_variant="content_2col",
                summary="Một flow gọn, dễ điều phối và đủ chiều sâu cho nhận thức lẫn hành động.",
                bullets=[
                    "Ice Break: 15 phút",
                    "Giới thiệu Psychological Safety: 15 phút",
                    "Game/Tình huống trải nghiệm: 30 phút",
                    "Thảo luận nhóm: 20 phút",
                ],
                key_message="Phần chia sẻ, tổng kết và cam kết hành động diễn ra ở nửa sau để chốt học tập.",
            ),
            SlideItem(
                title="Phần 1 - Ice Break tạo không khí an toàn",
                layout_variant="content_2col",
                summary="Mục tiêu là giảm căng thẳng, tạo cảm giác mọi ý kiến đều được chấp nhận và kích hoạt sự tham gia.",
                bullets=[
                    "Dùng Mentimeter hoặc polling ẩn danh để mọi người trả lời bằng điện thoại",
                    "Câu hỏi gợi ý: bạn có từng nghĩ 'ý kiến này thôi không nói thì hơn' không?",
                    "Câu hỏi gợi ý: khi mắc lỗi, điều bạn sợ nhất là gì?",
                    "Word Cloud: điều gì khiến bạn dễ lên tiếng nhất trong công việc?",
                ],
                key_message="MC chỉ công nhận kết quả, giữ trung lập và tuyệt đối tránh bình luận làm người tham gia co lại.",
            ),
            SlideItem(
                title="Phần 2 - Psychological Safety là gì?",
                layout_variant="comparison_before_after",
                summary="Đây là môi trường mọi người có thể phát biểu, hỏi và thừa nhận sai sót mà không sợ bị phủ nhận hay trừng phạt.",
                sections=[
                    {
                        "title": "KHÔNG phải",
                        "items": [
                            "Dễ dãi hoặc ai muốn làm gì thì làm",
                            "Không góp ý hay né tránh phản hồi",
                            "Giữ im lặng để tránh va chạm",
                        ],
                    },
                    {
                        "title": "Là",
                        "items": [
                            "Có thể nói thật và đặt câu hỏi",
                            "Có thể thử, sai và học hỏi",
                            "Có phản hồi nhưng không đe dọa giá trị con người",
                        ],
                    },
                ],
                key_message="Có thể nhắc Amy Edmondson và Google để tạo điểm neo đáng tin cậy cho khái niệm.",
            ),
            SlideItem(
                title="Phần 3 - Trải nghiệm qua 2 game",
                layout_variant="comparison_before_after",
                summary="Hai game đối lập giúp người tham gia cảm nhận rất rõ tác động của môi trường lên hành vi lên tiếng.",
                sections=[
                    {
                        "title": "Game 1: Cây tháp không được nói",
                        "items": [
                            "Mỗi nhóm dùng giấy, băng dính, ống hút hoặc que, kéo",
                            "Nhiệm vụ: xây tháp cao nhất trong 10 phút",
                            "Người chơi trực tiếp cảm nhận áp lực, khó giao tiếp và ngại lên tiếng",
                        ],
                    },
                    {
                        "title": "Game 2: Thành phố tương lai",
                        "items": [
                            "Mỗi nhóm xây một thành phố hoặc team lý tưởng trong tương lai",
                            "Cần trao đổi, lắng nghe, chia sẻ ý tưởng, phân công và hỗ trợ nhau",
                            "Psychological Safety xuất hiện tự nhiên qua teamwork và idea sharing",
                        ],
                    },
                ],
                key_message="Game 1 tạo sự gò bó; Game 2 mở ra cộng tác sáng tạo và cảm giác an toàn hơn.",
            ),
            SlideItem(
                title="Chuẩn bị cho 2 game",
                layout_variant="content_2col",
                summary="Chuẩn bị vật liệu đơn giản nhưng đủ để tạo trải nghiệm mạnh.",
                bullets=[
                    "Game 1: giấy, băng dính, ống hút hoặc que, kéo",
                    "Game 2: giấy màu, post-it, bút, ống hút, lego nếu có, băng dính, kéo",
                    "Mục tiêu Game 2: tạo một thành phố nơi mọi người muốn làm việc hoặc team lý tưởng trong tương lai",
                    "Điều phối viên cần quan sát hành vi lên tiếng, im lặng, lắng nghe và hỗ trợ",
                ],
            ),
            SlideItem(
                title="Phần 4 - Thảo luận nhóm sau trải nghiệm",
                layout_variant="comparison_before_after",
                summary="Đây là đoạn chuyển hóa trải nghiệm thành nhận thức hành vi và bài học cho team.",
                sections=[
                    {
                        "title": "Game 1",
                        "items": [
                            "Cảm giác thế nào?",
                            "Điều gì làm khó chịu?",
                            "Khi nào muốn im lặng?",
                        ],
                    },
                    {
                        "title": "Game 2",
                        "items": [
                            "Cảm giác thế nào?",
                            "Điều gì làm thoải mái?",
                            "Khi nào muốn đóng góp?",
                        ],
                    },
                ],
                key_message="Đừng dừng ở cảm xúc; hãy kéo người tham gia về câu hỏi: team đã vận hành ra sao trong từng bối cảnh?",
            ),
            SlideItem(
                title="Phần 5 - Xây dựng Rule of Safety",
                layout_variant="agenda",
                summary="Mỗi nhóm cùng tạo 5 nguyên tắc giúp team an toàn hơn và chọn nguyên tắc quan trọng nhất.",
                bullets=[
                    "Không cười nhạo ý kiến",
                    "Không ngắt lời",
                    "Sai thì sửa, không đổ lỗi",
                    "Hỏi để hiểu, không hỏi để bắt lỗi",
                    "Người quản lý phản hồi sau khi nghe hết",
                ],
                key_message="Hoạt động này tạo cảm giác cùng xây dựng văn hóa thay vì chỉ nghe lý thuyết.",
            ),
            SlideItem(
                title="Phần 6 - Cam kết hành động từ ngày mai",
                layout_variant="closing_cta",
                summary="Mỗi người tự ngẫm và viết ra hành động cụ thể cho chính mình, có thể ẩn danh nếu muốn.",
                key_message="Chuyển từ nhận thức sang hành vi nhỏ, rõ và thực hiện được ngay trong công việc hàng ngày.",
                bullets=[
                    "Ví dụ: hỏi ý kiến người ít nói hơn, không phản bác ngay, báo cáo sớm hơn khi có vấn đề, thừa nhận lỗi nhanh hơn",
                ],
                speaker_notes="Kết buổi bằng một lời mời cam kết ngắn: Tôi sẽ bắt đầu làm gì từ ngày mai để team an toàn hơn?",
            ),
        ],
    )


def main():
    output_path = Path("Workshop_Psychological_Safety.pptx").resolve()
    outline = build_outline()
    generator = PPTXGenerator(TEMPLATES["executive_blue"])
    result = generator.generate(outline, output_path)
    print(result)


if __name__ == "__main__":
    main()
