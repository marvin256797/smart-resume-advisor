from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("sample_resume.pdf", pagesize=letter)
c.drawString(100, 750, "John Doe")
c.drawString(100, 730, "Software Engineer")
c.drawString(100, 700, "Experience:")
c.drawString(100, 680, "- 3 years Python development")
c.drawString(100, 660, "- 2 years React frontend")
c.drawString(100, 640, "- Database management with PostgreSQL")
c.drawString(100, 610, "Skills:")
c.drawString(100, 590, "Python, JavaScript, React, PostgreSQL, Git, Docker")
c.save()
print("PDF created: sample_resume.pdf")