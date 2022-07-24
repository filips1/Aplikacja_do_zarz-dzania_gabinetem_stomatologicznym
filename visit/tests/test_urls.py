from django.test import SimpleTestCase
from django.urls import reverse, resolve
from visit.views import CalendarView, VisitUnaprovedShowView, VisitApprove, VisitReject, InfoView, InfoSeenView, InfoDeleteView



class TestUrls(SimpleTestCase):

    def test_calendar_url_is_resolved(self):
        url = reverse('calendar')
        self.assertEqual(resolve(url).func.view_class, CalendarView)






    def test_visit_approve_url_is_resolved(self):
        url = reverse('visit_approve',args="0")
        self.assertEqual(resolve(url).func, VisitApprove)


    def test_visit_reject_url_is_resolved(self):
        url = reverse('visit_reject',args="0")
        self.assertEqual(resolve(url).func, VisitReject)


    def test_unaproved_url_is_resolved(self):
        url = reverse('unaproved')
        self.assertEqual(resolve(url).func, VisitUnaprovedShowView)
        
    def test_info_url_is_resolved(self):
        url = reverse('info')
        self.assertEqual(resolve(url).func, InfoView)
                
    def test_info_seen_url_is_resolved(self):
        url = reverse('info_seen', args="0")
        self.assertEqual(resolve(url).func, InfoSeenView)
        
                
    def test_info_delete_url_is_resolved(self):
        url = reverse('info_delete', args="0")
        self.assertEqual(resolve(url).func, InfoDeleteView)
        

