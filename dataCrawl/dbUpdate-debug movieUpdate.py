from django.utils import timezone
from django.db import connections
from django.core.exceptions import ValidationError
from .models import movie, theater, showTimeInfo
from user.models import Movie as user_movie
from .datafrom import miramar, ambassador, viewshow, showtimes

# from .datafrom import showtimes_org as showtimes
from datetime import datetime
import pandas as pd
import re

def valid_data(your_objects,model):
    invalid_objects = []

    for obj in your_objects:
        print(obj,"處理中...")
        try:
            obj.full_clean()  # 驗證模型的所有約束
            model.objects.get_or_create(obj)
            print(obj,"完成")
        except ValidationError as e:
            invalid_objects.append(obj)
            print(f"Validation failed for object: {obj}, Error: {e}")
        except Exception as e:
            invalid_objects.append(obj)
            print(f"Error for object: {obj}, Error: {e}")

    return invalid_objects



def copy_movies():
    print("copy_movies starts") # Barry debug
    old_datas = list(user_movie.objects.values_list("title", flat=True).distinct())
    with connections["default"].cursor() as cursor:
        cursor.execute("SELECT title,img_src,trailer_link,movie_type,main_actor,info,release_date,running_time,screen_type FROM dataCrawl_movie")
        movies = cursor.fetchall()

    for movie in movies:
        if movie[0] in old_datas:
            continue
        print(movie[0],"處理中")
        movie_datas = user_movie(
            title=movie[0],
            img_src=movie[1],
            trailer_link=movie[2],
            movie_type=movie[3],
            main_actor=movie[4],
            info=movie[5],
            release_date=movie[6],
            running_time=movie[7],
            screen_type=movie[8],
        )
        movie_datas.save(using="second_db")


def extract_valid_times(input_string):
    # 定義正規表示式
    pattern = r"(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)"

    # 使用 re.findall 提取所有符合格式的部分
    valid_times = re.search(pattern, input_string)
    if valid_times:
        return valid_times.group()
    return None


today = datetime.today()
today = timezone.make_aware(today)


def movieUpdate(datas):
    # movie.objects.all().delete()
    moviesData = []
    movie_titles = [movie["title"] for movie in list(movie.objects.values("title"))]
    file = open("z:\\log.txt","w",encoding="utf-8") # Barry debug
    file.write("---------- datas 資料型別:"+str(type(datas))+" ----------\n")# Barry debug
    for i in datas:
        file.write(str(i)+"\n") # Barry debug
    file.write("----------------------------------------------------------------------"+"\n"*3) # Barry debug
    for data in datas:
        print(data["電影名稱"], "篩選中...")
        file.write("\n*****************************************************************************\n") # Barry debug
        file.write(data["電影名稱"]+" 篩選中...\n") # Barry debug
        try:
        ### 剛好遇到神奇字元所以replace...
            title = data["電影名稱"].replace("／", "/")
            file.write("title:"+str(title)+"\n") # Barry debug
            img_src = data["電影海報網址"][:100]
            file.write("img_src:"+str(img_src)+"\n") # Barry debug
            trailer_link = data["電影預告網址"][:100]
            file.write("trailer_link:"+str(trailer_link)+"\n") # Barry debug
            movie_type = data["影片類型"][:100]
            file.write("movie_type:"+str(movie_type)+"\n") # Barry debug
            main_actor = data["主要演員"][:100]
            file.write("main_actor:"+str(main_actor)+"\n") # Barry debug
            info = data["電影介紹"][:500]
            file.write("info:"+str(info)+"\n") # Barry debug
            release_date = data["上或待上映"][:100] if data["上或待上映"]!='未知' else None
            if release_date and '/' in release_date:
                release_date=release_date.replace('/','-')
            file.write("release_date:"+str(release_date)+"\n") # Barry debug
            running_time = data["電影時長"][:100]
            file.write("running_time:"+str(running_time)+"\n") # Barry debug
            screen_type = data["電影螢幕"]
            file.write("screen_type:"+str(screen_type)+"\n") # Barry debug

        except Exception as e:
            print(title, "輸入格式出現錯誤: ", str(e))
            file.write(str(title)+"輸入格式出現錯誤: \n") # Barry debug
            file.write("錯誤訊息：\n"+str(e)+"\n") # Barry debug
            continue
        if title in movie_titles or title in [movie.title for movie in moviesData]:
            print(title, "已存在")
            file.write(str(title)+"已存在") # Barry debug
            continue
        moviesData.append(
            movie(
                title=title,
                img_src=img_src,
                trailer_link=trailer_link,
                movie_type=movie_type,
                main_actor=main_actor,
                info=info,
                release_date=release_date,
                running_time=running_time,
                screen_type=screen_type,
            )
        )
    file1=open("z:\\moviesData.txt","w",encoding="utf-8") # Barry debug
    for j in moviesData: # Barry debug
        file1.write(f"Title: {j.title}\n") # Barry debug
        file1.write(f"Image Source: {j.img_src}\n") # Barry debug
        file1.write(f"Trailer Link: {j.trailer_link}\n") # Barry debug
        file1.write(f"Movie Type: {j.movie_type}\n") # Barry debug
        file1.write(f"Main Actor: {j.main_actor}\n") # Barry debug
        file1.write(f"Info: {j.info}\n") # Barry debug
        file1.write(f"Release Date: {j.release_date}\n") # Barry debug
        file1.write(f"Running Time: {j.running_time}\n") # Barry debug
        file1.write(f"Screen Type: {j.screen_type}\n") # Barry debug
        file1.write("\n" + "*"*77 + "\n"*2) # Barry debug
    file1.close() # Barry debug
    print("=========================== valid_data =================================") # Barry debug
    invalid=valid_data(moviesData,movie)
    print("========================================================================") # Barry debug
    print("無效資料: ",invalid)
    file.write("============================================================\n") # Barry debug
    file.write("無效資料: \n"+str(invalid)) # Barry debug
    file.write("============================================================\n") # Barry debug
    file.close() # Barry debug
    # movie.objects.bulk_create(valid)


def theaterUpdate(datas):
    theatersData = []
    theater_name = [theater["name"] for theater in list(theater.objects.values("name"))]
    for data in datas:
        name = data["戲院名稱"][:100]
        cinema = data["影城"][:100]
        address = data["影城位置"][:100]
        phone = data["影城電話"][:100]
        if name in theater_name or name in [theater.name for theater in theatersData]:
            continue
        theatersData.append(
            theater(name=name, cinema=cinema, address=address, phone=phone)
        )
    invalid=valid_data(theatersData,theater)
    print("無效資料: ",invalid)
    # theater.objects.bulk_create(valid)


def showUpdate(datas, is_limit=False):
    movies = {movie.title: movie for movie in movie.objects.all()}
    theaters = {theater.name: theater for theater in theater.objects.all()}
    showDatas = []
    # print(movies)
    # print(theaters)

    for i, data in enumerate(datas):
        # if is_limit and i > 500:
        #     break

        # 加入新電影
        print(data, "Running...")
        movieId = data["電影名稱"]
        theaterId = data["影城"]
        full_title = data["場次類型"] if "場次類型" in data else None
        date = data["日期"][:100]
        time = data["時間"][:100]
        time = extract_valid_times(time)
        site = data["廳位席位"][:100]
        try:
            print(movieId)
            movie_instance = movies[movieId] if movieId in movies else None
            theater_instance = theaters[theaterId] if theaterId in theaters else None
            if not movie_instance or not theater_instance:
                print(f"Movie or theater not found: {movieId}, {theaterId}")
                continue
            show_data = showTimeInfo(
                movie=movie_instance,
                theater=theater_instance,
                full_title=full_title,
                date=date,
                time=time,
                site=site,
            )
            if show_data in showDatas:
                continue
            showDatas.append(show_data)
        except Exception as e:
            print(movieId, "error!", str(e))
            continue

    print("預計上傳筆數: ", len(showDatas))
    # invalid=valid_data(showDatas,showTimeInfo)
    # print("無效資料: ",invalid)
    showTimeInfo.objects.bulk_create(showDatas)


### 下方為與爬蟲功能連結


def UpdateMovies():
    ### 秀泰
    sho_movies = showtimes.scrape_all_movies()
    ### 美麗華
    mir_movie = miramar.get_movie()
    ### 國賓
    amb_movie, amb_show = ambassador.get_movie_and_show()
    movies = pd.concat([sho_movies, mir_movie, amb_movie]).drop_duplicates(
        subset=["電影名稱"]
    )
    print("db duplicates is done") # Barry debug
    movies.to_csv("z:\\moviesPd.csv",encoding="utf-8-sig") # Barry debug
    # movies = amb_movie.drop_duplicates(subset=["電影名稱"])
    movieUpdate(movies.to_dict("records"))
    copy_movies()
    return {"result": "finish!"}


def UpdateShows():
    # 清除電影(date__lt表示小於特定日期)
    showTimeInfo.objects.all().delete()

    ### 秀泰
    sho_show = showtimes.scrape_show_info()
    ### 美麗華
    mir_show = miramar.get_showTimeInfo()
    ### 國賓
    amb_movie, amb_show = ambassador.get_movie_and_show()
    ### 威秀
    vie_show = viewshow.get_datas()

    shows = pd.concat([sho_show, mir_show, amb_show, vie_show]).drop_duplicates()
    print(shows)
    showUpdate(shows.to_dict("records"))
    return {"result": "finish!"}


def UpdateTheater(mode=""):
    ### 直接用csv
    if mode == "csv":
        df = pd.read_csv("staticfiles/csv/theaterInfo.csv")
        df = df.rename(
            columns={"戲院": "戲院名稱", "地址": "影城位置", "連絡電話": "影城電話"}
        )
        datas = df.to_dict("records")
        theaterUpdate(datas)

        return {"result": "finish!"}
    ### 秀泰
    df = showtimes.scrape_cinema_info()
    datas = df.to_dict("records")
    theaterUpdate(datas)

    ### 美麗華
    df = miramar.get_theater()
    datas = df.to_dict("records")
    theaterUpdate(datas)

    ### 國賓
    df = ambassador.get_theater()
    datas = df.to_dict("records")
    theaterUpdate(datas)

    return {"result": "finish!"}


if __name__ == "__main__":
    # UpdateTheater(mode='csv')
    pass
