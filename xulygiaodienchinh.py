
from datetime import datetime
from traceback import print_exc
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem

from Final_term_project.League import league, Players, History
from Final_term_project.UI.Main_Screen import Ui_MainWindow
from Final_term_project.tool.Xulygiaodienlogin import xulylogin, xulyregis
from Final_term_project.tool.xuly_search import xu_ly_search


class xulychinh(Ui_MainWindow):
    def setupUi(self, MainWindow):
        super().setupUi(MainWindow)
        self.MainWindow = MainWindow
    def showWindow(self):
        self.MainWindow.show()

    def setupSignalAndSlot(self):
        self.sign_in_button.clicked.connect(self.show_sign_in)
        self.login_button.clicked.connect(self.show_log_in)
        self.searchButton.clicked.connect(self.search)
        # Kết nối nút "Before" và "Next" cho Most Goals

    def show_rank(self, players):  # Chưa hiện được ds relegation
        self.ranking_tableWidget.setRowCount(len(players.team_list))  # Số hàng = số đội
        self.ranking_tableWidget.setColumnCount(5)
        league.update_standings()
        for row, team in enumerate(league.team_list):
            self.ranking_tableWidget.setItem(row, 0, QTableWidgetItem(team.name))
            self.ranking_tableWidget.setItem(row, 1, QTableWidgetItem(str(team.wins)))
            self.ranking_tableWidget.setItem(row, 2, QTableWidgetItem(str(team.loses)))
            self.ranking_tableWidget.setItem(row, 3, QTableWidgetItem(str(team.draws)))
            self.ranking_tableWidget.setItem(row, 4, QTableWidgetItem(str(team.point)))

    def show_upcoming_matches(self, upcomingmatches):
        # Lọc các trận đấu có score[0] = None
        filtered_matches = [match for match in upcomingmatches if match.score[0] is None]

        # Sắp xếp theo ngày (date) tăng dần
        filtered_matches.sort(key=lambda match: datetime.strptime(match.date, "%d/%m/%Y"))

        # Thiết lập bảng
        self.matchday_tableWidget.horizontalHeader().setStretchLastSection(True)
        self.matchday_tableWidget.setRowCount(len(filtered_matches))  # Số hàng = số trận đấu đã lọc
        self.matchday_tableWidget.setColumnCount(2)

        # Điền dữ liệu vào bảng
        for row, match in enumerate(filtered_matches):
            self.matchday_tableWidget.setItem(row, 0, QTableWidgetItem(match.date))
            self.matchday_tableWidget.setItem(row, 1, QTableWidgetItem(f"{match.teams[0]} vs {match.teams[1]}"))
    def show_sign_in(self):
        try:
            self.window = QMainWindow()
            self.ui = xulyregis()
            self.ui.setupUi(self.window)
            self.window.show()
        except:
            print_exc()

    def show_log_in(self):
        try:
            self.window = QMainWindow()
            self.ui = xulylogin()
            self.ui.setupUi(self.window)
            self.window.show()

            # Đảm bảo sự kiện chỉ được gán một lần
            try:
                self.ui.pushButton_login.clicked.disconnect()
            except TypeError:
                pass  # Nếu chưa có kết nối nào, bỏ qua lỗi

            self.ui.pushButton_login.clicked.connect(self.handle_login)

        except:
            print_exc()

    def handle_login(self):
        if self.ui.check_login():
            self.MainWindow.close()

    def search(self):
        try:
            self.search_term = self.searchLineEdit.text()
            self.window = QMainWindow()
            self.ui = xu_ly_search()
            self.ui.setupUi(self.window)
            self.ui.setupSignalandSlot()
            self.ui.searchLineEdit.setText(self.search_term)
            self.ui.search()
            self.window.show()
        except:
            print_exc()
    def most_scored(self):
        Players.load_player()
        if Players.player_list!=[]:
            top_scorer = max(Players.player_list, key=lambda player: player.goals) if max(Players.player_list, key=lambda player: player.goals) else None
            self.player_group_1.setTitle(top_scorer.name)
            self.team_label_1.setText(f"Team: {top_scorer.team}")
            self.goals_label_1.setText(f"Goals: {top_scorer.goals}")
            self.assists_label_1.setText(f"Assists: {top_scorer.assists}")
            self.position_label_1.setText(f"Position: {top_scorer.pos}")
            self.red_cards_label_1.setText(f"Red cards: {top_scorer.red}")
            self.yellow_cards_label_1.setText(f"Yellow cards: {top_scorer.yellow}")
            self.image_label_1.setScaledContents(True)
            self.image_label_1.setPixmap(QPixmap(top_scorer.pic))
    def most_assists(self):
        if Players.player_list != []:
            top_assist = max(Players.player_list, key=lambda player: player.assists)
            self.player_group_assists_1.setTitle(top_assist.name)
            self.team_label_assists_1.setText(f"Team: {top_assist.team}")
            self.goals_label_assists_1.setText(f"Goals: {top_assist.goals}")
            self.assists_label_assists_1.setText(f"Assists: {top_assist.assists}")
            self.position_label_assists_1.setText(f"Position: {top_assist.pos}")
            self.red_cards_label_assists_1.setText(f"Red cards: {top_assist.red}")
            self.yellow_cards_label_assists_1.setText(f"Yellow cards: {top_assist.yellow}")
            self.image_label_assists_1.setScaledContents(True)
            self.image_label_assists_1.setPixmap(QPixmap(top_assist.pic))

league.load_team()
Players.load_player()
Players.save_player()
app = QApplication([])
main_window = QMainWindow()
myWindow = xulychinh()
myWindow.setupUi(main_window)
myWindow.setupSignalAndSlot()
myWindow.show_rank(league)
myWindow.most_scored()
myWindow.most_assists()
myWindow.show_upcoming_matches(History.history)
myWindow.showWindow()
app.exec()

