"""
Système de statistiques pour les jeux Discord
Gère les scores, classements et statistiques des joueurs
"""
import aiosqlite
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class GameStatsManager:
    """Gestionnaire des statistiques de jeu"""
    
    def __init__(self, db_path: str = "shadow_roll.db"):
        self.db_path = db_path
        
    async def initialize_database(self):
        """Initialiser les tables des statistiques de jeu"""
        async with aiosqlite.connect(self.db_path) as db:
            # Table des statistiques globales par joueur
            await db.execute('''
                CREATE TABLE IF NOT EXISTS player_game_stats (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT NOT NULL,
                    total_wins INTEGER DEFAULT 0,
                    total_games INTEGER DEFAULT 0,
                    total_rounds INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0.0,
                    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table des parties individuelles
            await db.execute('''
                CREATE TABLE IF NOT EXISTS game_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    channel_id INTEGER NOT NULL,
                    game_type TEXT NOT NULL,
                    theme TEXT,
                    max_rounds INTEGER,
                    voting_time INTEGER,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    winner_id INTEGER,
                    total_participants INTEGER DEFAULT 0
                )
            ''')
            
            # Table des performances par partie
            await db.execute('''
                CREATE TABLE IF NOT EXISTS player_session_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    user_id INTEGER,
                    username TEXT,
                    correct_votes INTEGER DEFAULT 0,
                    total_votes INTEGER DEFAULT 0,
                    final_score INTEGER DEFAULT 0,
                    final_rank INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id)
                )
            ''')
            
            # Table des détails des manches
            await db.execute('''
                CREATE TABLE IF NOT EXISTS round_details (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    round_number INTEGER,
                    option_a TEXT,
                    option_b TEXT,
                    votes_a INTEGER DEFAULT 0,
                    votes_b INTEGER DEFAULT 0,
                    majority_option TEXT,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id)
                )
            ''')
            
            # Table des votes individuels
            await db.execute('''
                CREATE TABLE IF NOT EXISTS player_votes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER,
                    round_number INTEGER,
                    user_id INTEGER,
                    username TEXT,
                    voted_option TEXT,
                    was_majority INTEGER DEFAULT 0,
                    FOREIGN KEY (session_id) REFERENCES game_sessions(session_id)
                )
            ''')
            
            await db.commit()
            logger.info("Game statistics database initialized successfully")
    
    async def start_game_session(self, channel_id: int, game_type: str, theme: str = None, 
                                max_rounds: int = 5, voting_time: int = 10) -> int:
        """Commencer une nouvelle session de jeu"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                INSERT INTO game_sessions (channel_id, game_type, theme, max_rounds, voting_time)
                VALUES (?, ?, ?, ?, ?)
            ''', (channel_id, game_type, theme, max_rounds, voting_time))
            
            session_id = cursor.lastrowid
            await db.commit()
            logger.info(f"Started game session {session_id} in channel {channel_id}")
            return session_id
    
    async def end_game_session(self, session_id: int, winner_id: int = None, 
                              total_participants: int = 0):
        """Terminer une session de jeu"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE game_sessions 
                SET end_time = CURRENT_TIMESTAMP, winner_id = ?, total_participants = ?
                WHERE session_id = ?
            ''', (winner_id, total_participants, session_id))
            
            await db.commit()
            logger.info(f"Ended game session {session_id}")
    
    async def record_round_result(self, session_id: int, round_number: int, 
                                 option_a: str, option_b: str, 
                                 votes_a: int, votes_b: int):
        """Enregistrer les résultats d'une manche"""
        majority_option = "A" if votes_a > votes_b else "B"
        
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO round_details 
                (session_id, round_number, option_a, option_b, votes_a, votes_b, majority_option)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (session_id, round_number, option_a, option_b, votes_a, votes_b, majority_option))
            
            await db.commit()
    
    async def record_player_vote(self, session_id: int, round_number: int, 
                               user_id: int, username: str, voted_option: str,
                               was_majority: bool):
        """Enregistrer le vote d'un joueur"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO player_votes 
                (session_id, round_number, user_id, username, voted_option, was_majority)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (session_id, round_number, user_id, username, voted_option, int(was_majority)))
            
            await db.commit()
    
    async def calculate_session_scores(self, session_id: int) -> List[Tuple[int, str, int, int]]:
        """Calculer les scores finaux d'une session"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT user_id, username, 
                       SUM(was_majority) as correct_votes,
                       COUNT(*) as total_votes
                FROM player_votes 
                WHERE session_id = ?
                GROUP BY user_id, username
                ORDER BY correct_votes DESC, total_votes DESC
            ''', (session_id,))
            
            results = await cursor.fetchall()
            
            # Enregistrer les résultats dans player_session_stats
            for rank, (user_id, username, correct_votes, total_votes) in enumerate(results, 1):
                await db.execute('''
                    INSERT INTO player_session_stats 
                    (session_id, user_id, username, correct_votes, total_votes, final_score, final_rank)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (session_id, user_id, username, correct_votes, total_votes, correct_votes, rank))
            
            await db.commit()
            return results
    
    async def update_player_global_stats(self, user_id: int, username: str, 
                                        wins_gained: int, games_played: int = 1,
                                        rounds_played: int = 0):
        """Mettre à jour les statistiques globales d'un joueur"""
        async with aiosqlite.connect(self.db_path) as db:
            # Vérifier si le joueur existe
            cursor = await db.execute('''
                SELECT total_wins, total_games, total_rounds FROM player_game_stats
                WHERE user_id = ?
            ''', (user_id,))
            
            result = await cursor.fetchone()
            
            if result:
                # Mettre à jour les stats existantes
                total_wins, total_games, total_rounds = result
                new_total_wins = total_wins + wins_gained
                new_total_games = total_games + games_played
                new_total_rounds = total_rounds + rounds_played
                new_win_rate = (new_total_wins / new_total_rounds) if new_total_rounds > 0 else 0.0
                
                await db.execute('''
                    UPDATE player_game_stats 
                    SET username = ?, total_wins = ?, total_games = ?, total_rounds = ?,
                        win_rate = ?, last_played = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                ''', (username, new_total_wins, new_total_games, new_total_rounds, 
                     new_win_rate, user_id))
            else:
                # Créer de nouvelles stats
                win_rate = (wins_gained / rounds_played) if rounds_played > 0 else 0.0
                await db.execute('''
                    INSERT INTO player_game_stats 
                    (user_id, username, total_wins, total_games, total_rounds, win_rate)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, username, wins_gained, games_played, rounds_played, win_rate))
            
            await db.commit()
    
    async def get_player_stats(self, user_id: int) -> Optional[Dict]:
        """Récupérer les statistiques d'un joueur"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT username, total_wins, total_games, total_rounds, win_rate, last_played
                FROM player_game_stats
                WHERE user_id = ?
            ''', (user_id,))
            
            result = await cursor.fetchone()
            if result:
                return {
                    'username': result[0],
                    'total_wins': result[1],
                    'total_games': result[2],
                    'total_rounds': result[3],
                    'win_rate': result[4],
                    'last_played': result[5]
                }
            return None
    
    async def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Récupérer le classement des meilleurs joueurs"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT username, total_wins, total_games, total_rounds, win_rate
                FROM player_game_stats
                WHERE total_rounds > 0
                ORDER BY win_rate DESC, total_wins DESC
                LIMIT ?
            ''', (limit,))
            
            results = await cursor.fetchall()
            return [
                {
                    'username': row[0],
                    'total_wins': row[1],
                    'total_games': row[2],
                    'total_rounds': row[3],
                    'win_rate': row[4]
                }
                for row in results
            ]
    
    async def get_session_history(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Récupérer l'historique des sessions d'un joueur"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute('''
                SELECT gs.game_type, gs.theme, pss.correct_votes, pss.total_votes, 
                       pss.final_rank, gs.total_participants, gs.start_time
                FROM player_session_stats pss
                JOIN game_sessions gs ON pss.session_id = gs.session_id
                WHERE pss.user_id = ?
                ORDER BY gs.start_time DESC
                LIMIT ?
            ''', (user_id, limit))
            
            results = await cursor.fetchall()
            return [
                {
                    'game_type': row[0],
                    'theme': row[1],
                    'correct_votes': row[2],
                    'total_votes': row[3],
                    'final_rank': row[4],
                    'total_participants': row[5],
                    'start_time': row[6]
                }
                for row in results
            ]