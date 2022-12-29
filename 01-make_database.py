import sqlite3

# 使用するエキスパンションをここで指定しておく
# TODO: あとで外部ファイルとかで管理するかも
ALLOW_LIST = ['LEA', '2ED', 'ARN', 'ATQ', '3ED', 'LEG', 'DRK', 'PHPR', 'FEM',
              '4ED', 'ICE', 'HML', 'ALL', 'MIR', 'VIS', '5ED', 'POR', 'WTH',
              'TMP', 'STH', 'EXO', 'P02', 'USG', 'ULG', '6ED', 'UDS', 'S99',
              'PTK', 'MMQ', 'NEM', 'PCY', 'INV', 'PLS', '7ED', 'APC', 'ODY',
              'TOR', 'JUD', 'ONS', 'LGN', 'SCG', '8ED', 'MRD', 'DST', '5DN',
              'CHK', 'BOK', 'SOK', '9ED', 'RAV', 'GPT', 'DIS', 'CSP', 'TSP',
              'PLC', 'FUT', '10E', 'LRW', 'MOR', 'SHM', 'EVE', 'ALA', 'CON',
              'ARB', 'M10', 'ZEN', 'WWK', 'ROE', 'M11', 'SOM', 'MBS', 'NPH',
              'CMD', 'M12', 'ISD', 'DKA', 'AVR', 'PC2', 'M13', 'RTR', 'GTC',
              'DGM', 'M14', 'THS', 'C13', 'BNG', 'JOU', 'CNS', 'M15', 'KTK',
              'C14', 'FRF', 'DTK', 'ORI', 'BFZ', 'C15', 'OGW', 'SOI', 'EMN',
              'CN2', 'KLD', 'C16', 'AER', 'AKH', 'HOU', 'C17', 'XLN', 'RIX',
              'DOM', 'BBD', 'GS1', 'M19', 'C18', 'GRN', 'GNT', 'G18', 'RNA',
              'WAR', 'MH1', 'M20', 'C19', 'ELD', 'GN2', 'THB', 'C20', 'IKO',
              'M21', 'JMP', 'ZNR', 'ZNC', 'CMR', 'KHM', 'KHC', 'STX', 'C21',
              'MH2', 'AFR', 'AFC', 'MID', 'MIC', 'VOW', 'VOC', 'NEO', 'NEC',
              'SNC', 'NCC', 'CLB', 'DMU', '40K', 'UNF', 'GN3', 'BRO', 'J22',
              'SLD'] # ONE, ONC

path_db_orig = './data/db/AllPrintings.sqlite'
path_db_kamir = './data/db/kamir_cardpool.sqlite'

def make_database():
    # データ作成用にデータをかいつまんだsqliteデータベースを作成する
    conn = sqlite3.connect(path_db_kamir)
    cur = conn.cursor()

    cur.execute("ATTACH DATABASE '{}' AS source;".format(path_db_orig))

    cur.execute("DROP TABLE IF EXISTS main.meta")
    cur.execute("CREATE TABLE meta AS SELECT * FROM source.meta")

    # kamir_cardpool.sqliteを直接開いて確認するとき用のテーブル
    # cur.execute("DROP TABLE IF EXISTS main.cards_orig")
    # cur.execute("CREATE TABLE main.cards_orig AS SELECT * FROM source.cards;")

    # cardsテーブルのスキーム設定
    cur.execute("DROP TABLE IF EXISTS main.cards")
    # cur.execute(
    #     """
    #     CREATE TABLE cards(
    #         name STRING PRIMARY KEY,
    #         name_image STRING,
    #         mana_value INTEGER,
    #         mana_cost STRING,
    #         type STRING,
    #         oracle TEXT,
    #         expansion STRING,
    #         expansion_id INTEGER,
    #         power STRING,
    #         toughness STRING,
    #         layout STRING,
    #         multiverse_id STRING,
    #         release_date TEXT
    #     )
    #     """
    # )
    cur.execute(
        """
        CREATE TABLE cards(
            name STRING PRIMARY KEY,
            mana_value INTEGER,
            mana_cost STRING,
            type STRING,
            oracle TEXT,
            expansion STRING,
            expansion_id INTEGER,
            power STRING,
            toughness STRING,
            layout STRING,
            multiverse_id STRING,
            release_date TEXT
        )
        """
    )

    # expansionsテーブルのスキーム設定
    cur.execute("DROP TABLE IF EXISTS main.expansions")
    cur.execute(
        """
        CREATE TABLE expansions(
            id integer primary key autoincrement,
            name string,
            name_code text,
            release_date text
        )
        """
    )

    # expansionsテーブルに使用するエキスパンション情報を挿入
    for exp in ALLOW_LIST:
        query = 'INSERT INTO expansions(name, name_code, release_date) SELECT name, code, releaseDate FROM source.sets WHERE code = "{}"'.format(exp)
        cur.execute(query)

    # cardsテーブルに使用するカード情報を挿入
    # cur.execute(
    #     """
    #     INSERT INTO cards
    #     (
    #         name,
    #         name_image,
    #         mana_value,
    #         mana_cost,
    #         type,
    #         oracle,
    #         expansion,
    #         expansion_id,
    #         power,
    #         toughness,
    #         layout,
    #         multiverse_id,
    #         release_date
    #     )
    #     SELECT
    #         name,
    #         name_image,
    #         manaValue,
    #         manaCost,
    #         REPLACE(type, '—', '-'),
    #         REPLACE(text, '•', '*'),
    #         setCode,
    #         id,
    #         power,
    #         toughness,
    #         layout,
    #         multiverseId,
    #         release_date
    #     FROM
    #     (
    #         SELECT
    #             COALESCE(c.asciiName, c.faceName, c.name) name,
    #             COALESCE(c.faceName, c.name) name_image,
    #             c.manaValue,
    #             c.manaCost,
    #             c.type,
    #             c.text,
    #             c.setCode,
    #             e.id,
    #             c.power,
    #             c.toughness,
    #             c.layout,
    #             c.multiverseId,
    #             e.release_date
    #         FROM source.cards c
    #         INNER JOIN main.expansions e
    #         ON c.setCode = e.name_code
    #         WHERE types LIKE "%Creature%" AND (side = "a" OR side IS NULL)
    #         ORDER BY e.id, c.name
    #     )
    #     GROUP BY name
    #     ORDER BY id, name
    #     """
    # )
    cur.execute(
        """
        INSERT INTO cards
        (
            name,
            mana_value,
            mana_cost,
            type,
            oracle,
            expansion,
            expansion_id,
            power,
            toughness,
            layout,
            multiverse_id,
            release_date
        )
        SELECT
            name,
            manaValue,
            manaCost,
            REPLACE(type, '—', '-'),
            REPLACE(text, '•', '*'),
            setCode,
            id,
            power,
            toughness,
            layout,
            multiverseId,
            release_date
        FROM
        (
            SELECT
                COALESCE(c.asciiName, c.faceName, c.name) name,
                c.manaValue,
                c.manaCost,
                c.type,
                c.text,
                c.setCode,
                e.id,
                c.power,
                c.toughness,
                c.layout,
                c.multiverseId,
                e.release_date
            FROM source.cards c
            INNER JOIN main.expansions e
            ON c.setCode = e.name_code
            WHERE
                types LIKE "%Creature%"
                AND (side = "a" OR side IS NULL)
                AND printf("%d", c.number) == c.number
                AND isFunny = 0
            ORDER BY e.id, c.name
        )
        GROUP BY name
        ORDER BY id, name
        """
    )

    cur.execute("UPDATE main.cards SET oracle=REPLACE(oracle,\"â\",\"a\")")
    cur.execute("UPDATE main.cards SET oracle=REPLACE(oracle,\"á\",\"a\")")
    # cur.execute("UPDATE main.cards SET oracle=REPLACE(oracle,\"à\",\"a\")") //  兄弟戦争現在Chicken à la Kingのみ該当、銀枠
    cur.execute("UPDATE main.cards SET oracle=REPLACE(oracle,\"í\",\"i\")")
    cur.execute("UPDATE main.cards SET oracle=REPLACE(oracle,\"ú\",\"u\")")
    cur.execute("UPDATE main.cards SET oracle=REPLACE(oracle,\"û\",\"u\")")
    cur.execute("UPDATE main.cards SET oracle=REPLACE(oracle,\"ñ\",\"n\")")
    cur.execute("UPDATE main.cards SET oracle=REPLACE(oracle,\"ö\",\"o\")")

    conn.commit()
    conn.close()


if __name__ == '__main__':
    make_database()