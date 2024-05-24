from fastapi import APIRouter
from src.modules.text_summarizer_service import service


router = APIRouter()


router.add_api_route('/generate-summary-via-url/', service.generate_summary_via_url_service, methods=["POST"])
router.add_api_route('/generate-summary-via-text/', service.generate_summary_via_text_service, methods=["POST"])
router.add_api_route('/generate-summary-flowchart/', service.generate_summary_flowchart_service, methods=["POST"])
router.add_api_route('/download-pdf/', service.download_pdf, methods=["POST"])
router.add_api_route('/text-to-speech/', service.text_to_speech_service, methods=["POST"])
router.add_api_route('/search-about/', service.search_about_service, methods=["POST"])
