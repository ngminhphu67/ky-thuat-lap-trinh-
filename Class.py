import hashlib
import json
import os
import uuid
from datetime import datetime, timedelta
from traceback import print_exc

from PyQt6.QtWidgets import QApplication

import hashlib
import uuid


class Users:
    def __init__(self, name, password=None, user_type="user", id=str(uuid.uuid4()), player_list=None, team_list=None, password_hash=None):
        self.id = id
        self.name = name
        if password_hash is not None:
            self.password_hash = password_hash
        else:
            self.password_hash = self.hash_password(password)
        self.player_list = player_list if player_list else []  # Danh sách đối tượng player
        self.team_list = team_list if team_list else []  # Danh sách tên đội bóng (chuỗi)
        self.user_type = user_type

    def hash_password(self, password):
        """Hàm tạo mã băm SHA-256 từ mật khẩu"""
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    def to_dict(self):
        return {
            "name": self.name,
            "password_hash": self.password_hash,
            "user_type": self.user_type,
            "id": self.id,
            "player_list": [player.to_dict() for player in self.player_list],
            "team_list": self.team_list
        }

    @staticmethod
    def from_dict(data):
        player_list_data = data.get("player_list", [])
        player_list = []
        for item in player_list_data:
            if isinstance(item, dict):
                # Nếu là dictionary, tạo player từ dữ liệu đầy đủ
                player_list.append(player.from_dict(item))
            elif isinstance(item, str):
                # Nếu là chuỗi (dữ liệu cũ), tạo player với giá trị mặc định
                player_list.append(player(
                    name=item,
                    number="0",
                    pos="Unknown",
                    con_count=0,
                    team="Unknown"
                ))
            else:
                continue

        return Users(
            name=data["name"],
            user_type=data["user_type"],
            id=data["id"],
            player_list=player_list,  # Danh sách đối tượng player
            team_list=data.get("team_list", []),  # Danh sách tên đội bóng (chuỗi)
            password_hash=data["password_hash"]
        )

    def add_player(self, player_obj):
        """Thêm cầu thủ vào danh sách, không thêm nếu đã tồn tại"""
        if not isinstance(player_obj, player):
            raise ValueError("Tham số phải là một đối tượng player")
        # Kiểm tra xem cầu thủ đã tồn tại chưa (dựa trên name và team)
        for existing_player in self.player_list:
            if existing_player.name == player_obj.name and existing_player.team == player_obj.team:
                return False  # Đã tồn tại, không thêm
        self.player_list.append(player_obj)
        return True  # Thêm thành công

    def add_team(self, team_name):
        """Thêm đội bóng vào danh sách, không thêm nếu đã tồn tại"""
        if not isinstance(team_name, str):
            raise ValueError("Tham số phải là một chuỗi (tên đội bóng)")
        # Kiểm tra xem đội bóng đã tồn tại chưa
        if team_name in self.team_list:
            return False  # Đã tồn tại, không thêm
        self.team_list.append(team_name)
        return True  # Thêm thành công
    def del_team(self,team_name):
        for team in self.team_list:
            if team==team_name:
                self.team_list.remove(team)
    def del_player(self,player):
        for fav_player in self.player_list:
            if fav_player.name==player.name and fav_player.team == player.team and fav_player.number==player.number:
                self.player_list.remove(player)
class User_list:
    def __init__(self, filename="user_list.json"):
        self.filename = filename
        self.user_list = self.load_users()

    def save_users(self):
        """Lưu danh sách user vào file JSON"""
        with open(self.filename, "w") as f:
            json.dump([user.to_dict() for user in self.user_list], f, indent=4)

    def load_users(self):
        """Đọc danh sách user từ file JSON"""
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                return [Users.from_dict(user) for user in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def add_user(self, register):
        try:
            for use in self.user_list:
                if use.name == register.name:
                    return False  # Trả về False nếu tìm thấy người dùng trùng tên
            self.user_list.append(register)
            self.save_users()
            print(self.user_list)
            return True  # Trả về True nếu đã thêm thành công
        except:
            print_exc()

    def check_login(self, user, pas):
        """Kiểm tra đăng nhập bằng SHA-256"""
        input_hash = hashlib.sha256(pas.encode('utf-8')).hexdigest()
        for name in self.user_list:
            if name.name == user and name.password_hash == input_hash:
                return True, name
        return False, ""
    def remove_admin(self, id):
        for user in self.user_list:
            if user.id == id:
                user.user_type = "user"

    def add_admin(self, id):
        for user in self.user_list:
            if user.id == id:
                user.user_type = "admin"
class History:
    def __init__(self, filename="match_list.json"):
        self.upcomming_matches = []
        self.filename = filename
        self.history = self.load_matches()
    def save_matches(self):
        with open(self.filename, "w") as f:
            json.dump([user.to_dict() for user in self.history], f, indent=4)
    def load_matches(self):
        """ Đọc danh sách user từ file JSON """
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r") as f:
                data = json.load(f)
                return [matches.from_dict(match) for match in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    def add_matches(self,match):
        self.history.append(match)
    def sort_upcomming_matches(self):  # Hoặc get_upcoming_matches
        self.upcomming_matches = []
        for match in self.history:
            match_date = datetime.strptime(match.date, "%d/%m/%Y")  # Sửa thành dd/mm/yyyy
            if match_date >= datetime.today() + timedelta(days=14):
                self.upcomming_matches.append(match)
        return self.upcomming_matches
class League:
    def __init__(self, filename="team_list.json"):
        self.filename=filename
        self.team_list = self.load_team()

    def load_team(self):
        """
        Đọc danh sách đội bóng từ tệp JSON và trả về danh sách các đối tượng Team.
        """
        if not os.path.exists(self.filename):
            print(f"Không tìm thấy tệp {self.filename}. Trả về danh sách rỗng.")
            return []

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    print(f"Dữ liệu trong {self.filename} không phải là danh sách. Trả về danh sách rỗng.")
                    return []

                teams = []
                for team_data in data:
                    try:
                        team = Team.from_dict(team_data)
                        teams.append(team)
                    except (KeyError, TypeError) as e:
                        print(f"Lỗi khi chuyển đổi dữ liệu đội bóng: {e}. Bỏ qua mục này.")
                        continue

                print(f"Đã đọc thành công {len(teams)} đội từ {self.filename}.")
                return teams

        except json.JSONDecodeError as e:
            print(f"Lỗi giải mã JSON trong {self.filename}: {e}. Trả về danh sách rỗng.")
            return []
        except FileNotFoundError:
            print(f"Không thể mở tệp {self.filename}. Trả về danh sách rỗng.")
            return []
        except Exception as e:
            print(f"Lỗi không xác định khi đọc {self.filename}: {e}. Trả về danh sách rỗng.")
            return []
    def check_player(self,player):
        for team in self.team_list:
            if team.name==player.name:
                team.player_list.append(player)

    def save_team(self):
        """
        Lưu danh sách đội bóng vào tệp JSON với mã hóa UTF-8 và không thoát ký tự Unicode.
        """
        if not self.team_list:
            print("Warning: Không có đội nào trong danh sách. Không ghi vào file để tránh mất dữ liệu.")
            return

        try:
            unique_teams = []
            seen = set()
            for team in self.team_list:
                if team.name not in seen:
                    unique_teams.append(team)
                    seen.add(team.name)

            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([team.to_dict() for team in unique_teams], f, ensure_ascii=False, indent=4)
            print(f"Đã lưu thành công {len(unique_teams)} đội vào {self.filename}.")

        except Exception as e:
            print(f"Lỗi khi lưu tệp {self.filename}: {e}")
    def update_standings(self):
        self.team_list.sort(key=lambda team: team.point, reverse=True)
    def add_team(self,team):
        self.team_list.append(team)

    def sort_team(self, team_list, name, wins, loses, draws):
        try:
            filtered_teams = []
            for team in team_list:
                # Kiểm tra None trước khi sử dụng .strip() hoặc .lower()
                match_name = (name.strip().lower() in team.name.strip().lower()) if name and team.name else True
                match_wins = int(wins) >= team.wins if wins.isdigit() else True
                match_loses = int(loses) >= team.loses if loses.isdigit() else True
                match_draws=int(draws) >= team.draws if draws.isdigit() else True

                # Nếu tất cả điều kiện đều khớp, thêm đội vào danh sách lọc
                if match_name and match_wins and match_loses and match_draws:
                    filtered_teams.append(team)

            return filtered_teams
        except:
            print_exc()
            return []  # Trả về danh sách rỗng nếu có lỗi

    def del_team(self, name):
        # Xóa cầu thủ từ danh sách player_list
        self.team_list = [t for t in self.team_list if
                            not (t.name == name)]
        # Lưu lại danh sách cầu thủ sau khi xóa
        self.save_team()

class player:
    def __init__(self, name, number, pos, con_count, team, appear=0,goals=0, assists=0, achive="", red=0, yellow=0
                 , pic=r"D:\DaoTheKhai_K234111339\Final_term_project\player_image\default.jpg"):
        self.name = name          # Tên cầu thủ
        self.number = str(number)    # Số áo
        self.pos = pos            # Vị trí thi đấu
        self.goals = goals        # Số bàn thắng
        self.assists = assists    # Số pha kiến tạo
        self.red = red            # Thẻ đỏ
        self.yellow = yellow      # Thẻ vàng
        self.con_count = con_count  # Số năm hợp đồng còn lại
        self.team = team
        self.appear=appear# Đội bóng
        self.achive = achive      # Thành tích
        self.pic = pic            # Đường dẫn ảnh
    def update(self,appeared=False,scored=False,assisted=False,yellow=False,red=False):
        if appeared:
            self.appear+=1
        if scored:
            self.goals+=1
        if assisted:
            self.assists+=1
        if yellow:
            self.yellow+=1
        if red:
            self.red+=1
    def to_dict(self):
        return {
            "name": self.name,
            "number": self.number,
            "pos": self.pos,
            "contract": self.con_count,
            "team": self.team,
            "appear":self.appear,
            "goals": self.goals,
            "assists": self.assists,
            "achievements": self.achive,
            "red": self.red,
            "yellow": self.yellow,
            "picture": self.pic
        }
    @staticmethod
    def from_dict(data):
        """Tạo đối tượng player từ dictionary"""
        return player(
            name=data.get("name", ""),
            number=data.get("number", 0),
            pos=data.get("pos", ""),
            con_count=data.get("contract", 0),
            team=data.get("team", ""),
            appear=data.get("appear",0),
            goals=data.get("goals", 0),
            assists=data.get("assists", 0),
            achive=data.get("achievements", ""),
            red=data.get("red", 0),
            yellow=data.get("yellow", 0),
            pic=data.get("picture", r"D:\\DaoTheKhai_K234111339\\Final_term_project\\player_image\\default.jpg")
        )

    def __str__(self):
        return f"Player: {self.name}, Number: {self.number}, Position: {self.pos}, Goal: {self.goals}, Red:{self.red},Yellow:{self.yellow}"

class players:
    def __init__(self,filename="player_list.json"):
        self.filename = filename
        self.player_list=self.load_player()

    def add_player(self, new_player):
        # Kiểm tra xem cầu thủ đã tồn tại chưa
        if any(p.name == new_player.name and p.team == new_player.team for p in self.player_list):
            print(f"Cầu thủ {new_player.name} đã tồn tại trong đội {new_player.team}. Không thêm lại.")
            return
        self.player_list.append(new_player)

    def del_player(self, player_name, team_name,shirt_number, league):
        # Xóa cầu thủ từ danh sách player_list
        self.player_list = [p for p in self.player_list if not (p.name == player_name and p.team == team_name and p.number==shirt_number)]
        # Cập nhật danh sách cầu thủ trong các đội bóng
        for team in league.team_list:
            if team.name == team_name:
                team.player_list = [p for p in team.player_list if p != player_name]
        # Lưu lại danh sách cầu thủ sau khi xóa
        self.save_player()
        league.save_team()  # Lưu lại danh sách đội bóng sau khi cập nhật

    def sort_player(self,player_list, name, number, pos, con_count, team,appear, goals, assists, red, yellow):
        try:
            # Lọc danh sách cầu thủ dựa trên các thông tin được cung cấp
            filtered_players = []
            for player in player_list:
                # Kiểm tra từng điều kiện lọc
                match_name = name.lower() in player.name.lower() if name else True
                match_number = str(number) == str(player.number) if number else True
                match_pos = pos.lower() in player.pos.lower() if pos else True
                match_con_count = str(con_count) == str(player.con_count) if con_count else True
                match_team = team.lower() in player.team.lower() if team else True
                match_goals = str(goals) == str(player.goals) if goals else True
                match_assists = str(assists) <= str(player.assists) if assists else True
                match_red = str(red) <= str(player.red) if red else True
                match_yellow = str(yellow) <= str(player.yellow) if yellow else True
                match_appear = str(appear) <= str(player.appear) if appear else True
                # Nếu tất cả điều kiện đều khớp, thêm cầu thủ vào danh sách lọc
                if (match_name and match_number and match_pos and match_con_count and
                        match_team and match_goals and match_assists and
                        match_red and match_yellow and match_appear):
                    filtered_players.append(player)
            return filtered_players

        except:
            print_exc()
            return []  # Trả về danh sách rỗng nếu có lỗi

    def load_player(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, "r",encoding="utf-8") as f:
                data = json.load(f)
                return [player.from_dict(players) for players in data]
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_player(self):
        """
        Lưu danh sách cầu thủ vào tệp JSON với mã hóa UTF-8 và không thoát ký tự Unicode.
        """
        try:
            unique_players = []
            seen = set()
            for p in self.player_list:
                key = (p.name, p.team)
                if key not in seen:
                    unique_players.append(p)
                    seen.add(key)

            with open(self.filename, "w", encoding="utf-8") as f:
                json.dump([p.to_dict() for p in unique_players], f, ensure_ascii=False, indent=4)
            print(f"Đã lưu thành công {len(unique_players)} cầu thủ vào {self.filename}.")

        except Exception as e:
            print(f"Lỗi khi lưu tệp {self.filename}: {e}")

class matches:
    def __init__(self,date, teams=None, score=None,lineup1=None,lineup2=None,scorer1=None,scorer2=None, assistor1=None, assistor2=None,red=None,yellow=None,subs1=None,subs2=None):
        # 2 teams
        self.date=date
        self.teams = teams if teams else []  # Danh sách các đội
        # Scoreboard
        self.score = score if score else []  # Tỉ số trận đấu
        self.lineup1= lineup1 if lineup1 else []
        self.lineup2 = lineup2 if lineup2 else []
        self.scorer1=scorer1 if scorer1 else []
        self.scorer2=scorer2 if scorer2 else []
        self.assistor1 = assistor1 if assistor1 else []
        self.assistor2 = assistor2 if assistor2 else[]
        self.red=red if red else[]
        self.yellow=yellow if yellow else []
        self.subs1=subs1 if subs1 else []
        self.subs2=subs2 if subs2 else []
    def to_dict(self):
        return {"date":self.date,
            "teams": self.teams,
            "score": self.score,
            "lineup1": self.lineup1,
            "lineup2": self.lineup2,
            "scorer_1": self.scorer1,
            "scorer_2":self.scorer2,
            "assistor_1": self.assistor1,
            "assistor_2": self.assistor2,
            "Red":self.red,
            "Yellow":self.yellow,
            "Subs1":self.subs1,
            "Subs2":self.subs2}
    def from_dict(data):
        return matches(
            date=data["date"],
            teams=data["teams"],
            score=data["score"],
            lineup1=data["lineup1"],
            lineup2=data["lineup2"],
            scorer1 = data["scorer_1"],
            scorer2=data["scorer_2"],
            assistor1 =data["assistor_1"],
            assistor2 =data["assistor_2"],
            red=data["Red"],
            yellow=data["Yellow"],
            subs1=data["Subs1"],
            subs2=data["Subs2"])
class Team:
    def __init__(self,name,wins=0,loses=0,draws=0,pic_path = "D:\\DaoTheKhai_K234111339\\Final_term_project\\player_image\\default.jpg",player_list=None,match_history=None, file_name= "team_list.json",scored=0,goals_conceded=0):
        self.pic_path=pic_path
        self.name=name
        self.player_list = player_list if player_list else []
        self.wins = wins
        self.loses = loses
        self.draws = draws
        self.point=self.wins*3+self.draws
        self.match_hisrory=match_history if match_history else None
        self.filename=file_name
        self.scored=scored
        self.goals_conceded = goals_conceded
        self.hieuso=self.scored - self.goals_conceded
    def add_player(self,player):
        self.player_list.append(player)
    def to_dict(self):
        return {"Name": self.name,
            "wins": self.wins,
            "loses": self.loses,
            "draws":self.draws,
            "players":self.player_list,
            "pic_path":self.pic_path,
            "scored":self.scored,
            "goals_concede":self.goals_conceded}
    def from_dict(data):
        return Team(
            name=data["Name"],
            wins=data["wins"],
            loses=data["loses"],
            draws=data["draws"],
            player_list=data["players"],
            pic_path=data["pic_path"],
            scored = data["scored"],
            goals_conceded=data["goals_concede"])
def close_all_except(keep_window):
    for widget in QApplication.topLevelWidgets():
        if widget != keep_window:
            widget.close()