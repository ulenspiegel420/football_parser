from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QMovie, QPainter, QFontMetrics


class QTextMovieLabel(QLabel):
    def __init__(self, text, file_name):
        super().__init__(self)

        self._text = text

        m = QMovie(file_name)
        m.start()
        self.setMovie(m)

    def setMovie(self, movie):
        super().setMovie(movie)
        s = movie.currentImage().size()
        self._movieWidth = s.Width()
        self._movieHeight = s.Height()

    def paintEvent(self, evt):
        super().paintEvent(self, evt)
        p = QPainter(self)
        p.setFont(self.font())
        x = self._movieWidth + 6
        y = (self.height()+p.fontMetrics().xHeight())/2
        p.drawText(x,y,self._text)
        p.end()

    def sizeHint(self):
        fm = QFontMetrics(self.font())
        return QSize(self._movieWidth+6+fm.width(self._text), self._movieHeight)

    def setText(self, text):
        self._text = text