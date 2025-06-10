"""
Database module.

This module handles database connections and operations.
"""
import logging
import psycopg2
from psycopg2.extras import Json
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the database connection with the given configuration.
        
        Args:
            config: Configuration dictionary containing database connection settings
        """
        self.config = config
        self.db_host = config.get('db_host', 'localhost')
        self.db_port = config.get('db_port', '5432')
        self.db_name = config.get('db_name', 'thoughts_db')
        self.db_user = config.get('db_user', 'postgres')
        self.db_password = config.get('db_password', 'postgres')
        
        logger.info(f"Database initialized with host: {self.db_host}, port: {self.db_port}, database: {self.db_name}")
        
        # Create the table if it doesn't exist
        self._create_tables()
    
    def _get_connection(self):
        """
        Get a connection to the database.
        
        Returns:
            A database connection
        """
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
    
    def _create_tables(self):
        """
        Create the necessary tables if they don't exist.
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Create thoughts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS thoughts (
                    id SERIAL PRIMARY KEY,
                    transcription TEXT NOT NULL,
                    processed TEXT,
                    categories TEXT[],
                    tags TEXT[],
                    type TEXT,
                    priority TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create procedures table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS procedures (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    trigger_phrases TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create procedure steps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS procedure_steps (
                    id SERIAL PRIMARY KEY,
                    procedure_id INTEGER NOT NULL REFERENCES procedures(id) ON DELETE CASCADE,
                    content TEXT NOT NULL,
                    "order" INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(procedure_id, "order")
                )
            """)
            
            # Create technical_decisions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS technical_decisions (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    context TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    reasoning TEXT NOT NULL,
                    alternatives JSONB,
                    consequences TEXT[],
                    tags TEXT[],
                    related_resources TEXT[],
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Create experiences table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS experiences (
                    id SERIAL PRIMARY KEY,
                    title TEXT NOT NULL,
                    situation TEXT NOT NULL,
                    actions TEXT[],
                    outcome TEXT NOT NULL,
                    learnings TEXT[],
                    context TEXT,
                    tags TEXT[],
                    related_resources TEXT[],
                    importance TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {str(e)}")
    
    def save_thought(self, original_text: str, analysis_result: Dict[str, Any]) -> Optional[int]:
        """
        Save a thought to the database.
        
        Args:
            original_text: The original thought text
            analysis_result: The analysis result from the text analyzer
            
        Returns:
            The ID of the saved thought, or None if there was an error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert the thought
            cursor.execute(
                """
                INSERT INTO thoughts (
                    transcription,
                    processed,
                    categories,
                    tags,
                    type,
                    priority,
                    summary
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    original_text,
                    analysis_result.get('processed', ''),
                    analysis_result.get('categories', []),
                    analysis_result.get('tags', []),
                    analysis_result.get('type', ''),
                    analysis_result.get('priority', None),
                    analysis_result.get('summary', '')
                )
            )
            
            thought_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Thought saved with ID: {thought_id}")
            return thought_id
        except Exception as e:
            logger.error(f"Error saving thought to database: {str(e)}")
            return None
    
    def get_thought(self, thought_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a thought from the database by ID.
        
        Args:
            thought_id: The ID of the thought to get
            
        Returns:
            A dictionary containing the thought data, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 
                    id, 
                    transcription, 
                    processed, 
                    categories, 
                    tags, 
                    type, 
                    priority, 
                    summary, 
                    created_at
                FROM thoughts
                WHERE id = %s
                """,
                (thought_id,)
            )
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return {
                    'id': row[0],
                    'transcription': row[1],
                    'processed': row[2],
                    'categories': row[3],
                    'tags': row[4],
                    'type': row[5],
                    'priority': row[6],
                    'summary': row[7],
                    'created_at': row[8]
                }
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting thought from database: {str(e)}")
            return None
    
    def get_thoughts(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get multiple thoughts from the database.
        
        Args:
            limit: Maximum number of thoughts to return
            offset: Number of thoughts to skip
            
        Returns:
            A list of dictionaries containing thought data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 
                    id, 
                    transcription, 
                    processed, 
                    categories, 
                    tags, 
                    type, 
                    priority, 
                    summary, 
                    created_at
                FROM thoughts
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset)
            )
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            thoughts = []
            for row in rows:
                thoughts.append({
                    'id': row[0],
                    'transcription': row[1],
                    'processed': row[2],
                    'categories': row[3],
                    'tags': row[4],
                    'type': row[5],
                    'priority': row[6],
                    'summary': row[7],
                    'created_at': row[8]
                })
            
            return thoughts
        except Exception as e:
            logger.error(f"Error getting thoughts from database: {str(e)}")
            return []
            
    # Procedure-related methods
    def create_procedure(self, title: str, description: Optional[str] = None, trigger_phrases: List[str] = None) -> Optional[int]:
        """
        Create a new procedure in the database.
        
        Args:
            title: The title of the procedure
            description: Optional description of the procedure
            trigger_phrases: Optional list of trigger phrases
            
        Returns:
            The ID of the created procedure, or None if there was an error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert the procedure
            cursor.execute(
                """
                INSERT INTO procedures (
                    title,
                    description,
                    trigger_phrases
                ) VALUES (%s, %s, %s)
                RETURNING id
                """,
                (title, description, trigger_phrases or [])
            )
            
            procedure_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Procedure created with ID: {procedure_id}")
            return procedure_id
        except Exception as e:
            logger.error(f"Error creating procedure: {str(e)}")
            return None
    
    def get_procedures(self, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get multiple procedures from the database.
        
        Args:
            limit: Maximum number of procedures to return
            offset: Number of procedures to skip
            
        Returns:
            A list of dictionaries containing procedure data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get procedures with step count
            cursor.execute(
                """
                SELECT 
                    p.id, 
                    p.title, 
                    p.description, 
                    p.trigger_phrases, 
                    p.created_at,
                    COUNT(s.id) as step_count
                FROM procedures p
                LEFT JOIN procedure_steps s ON p.id = s.procedure_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset)
            )
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            procedures = []
            for row in rows:
                procedures.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'trigger_phrases': row[3],
                    'created_at': row[4],
                    'step_count': row[5]
                })
            
            return procedures
        except Exception as e:
            logger.error(f"Error getting procedures from database: {str(e)}")
            return []
    
    def get_procedure(self, procedure_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a procedure by ID with its steps.
        
        Args:
            procedure_id: The ID of the procedure to get
            
        Returns:
            A dictionary containing the procedure data, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get procedure
            cursor.execute(
                """
                SELECT 
                    id, 
                    title, 
                    description, 
                    trigger_phrases, 
                    created_at
                FROM procedures
                WHERE id = %s
                """,
                (procedure_id,)
            )
            
            procedure_row = cursor.fetchone()
            
            if not procedure_row:
                cursor.close()
                conn.close()
                return None
            
            procedure = {
                'id': procedure_row[0],
                'title': procedure_row[1],
                'description': procedure_row[2],
                'trigger_phrases': procedure_row[3],
                'created_at': procedure_row[4],
                'steps': []
            }
            
            # Get steps for the procedure
            cursor.execute(
                """
                SELECT 
                    id, 
                    procedure_id, 
                    content, 
                    "order", 
                    created_at
                FROM procedure_steps
                WHERE procedure_id = %s
                ORDER BY "order" ASC
                """,
                (procedure_id,)
            )
            
            step_rows = cursor.fetchall()
            
            for step_row in step_rows:
                procedure['steps'].append({
                    'id': step_row[0],
                    'procedure_id': step_row[1],
                    'content': step_row[2],
                    'order': step_row[3],
                    'created_at': step_row[4]
                })
            
            cursor.close()
            conn.close()
            
            return procedure
        except Exception as e:
            logger.error(f"Error getting procedure from database: {str(e)}")
            return None
    
    def add_procedure_step(self, procedure_id: int, content: str, order: int) -> Optional[int]:
        """
        Add a step to a procedure.
        
        Args:
            procedure_id: The ID of the procedure
            content: The content of the step
            order: The order of the step
            
        Returns:
            The ID of the created step, or None if there was an error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert the step
            cursor.execute(
                """
                INSERT INTO procedure_steps (
                    procedure_id,
                    content,
                    "order"
                ) VALUES (%s, %s, %s)
                RETURNING id
                """,
                (procedure_id, content, order)
            )
            
            step_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Procedure step created with ID: {step_id}")
            return step_id
        except Exception as e:
            logger.error(f"Error adding procedure step: {str(e)}")
            return None
    
    def add_procedure_steps(self, procedure_id: int, steps: List[Dict[str, Any]]) -> List[int]:
        """
        Add multiple steps to a procedure.
        
        Args:
            procedure_id: The ID of the procedure
            steps: List of step dictionaries with content and order
            
        Returns:
            List of created step IDs
        """
        step_ids = []
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            for step in steps:
                # Insert the step
                cursor.execute(
                    """
                    INSERT INTO procedure_steps (
                        procedure_id,
                        content,
                        "order"
                    ) VALUES (%s, %s, %s)
                    RETURNING id
                    """,
                    (procedure_id, step['content'], step['order'])
                )
                
                step_id = cursor.fetchone()[0]
                step_ids.append(step_id)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Added {len(step_ids)} steps to procedure {procedure_id}")
            return step_ids
        except Exception as e:
            logger.error(f"Error adding procedure steps: {str(e)}")
            return step_ids
    
    def delete_thought(self, thought_id: int) -> bool:
        """
        Delete a thought from the database.
        
        Args:
            thought_id: The ID of the thought to delete
            
        Returns:
            True if the thought was deleted, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete the thought
            cursor.execute(
                """
                DELETE FROM thoughts
                WHERE id = %s
                RETURNING id
                """,
                (thought_id,)
            )
            
            deleted = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if deleted:
                logger.info(f"Thought with ID {thought_id} deleted successfully")
                return True
            else:
                logger.warning(f"Thought with ID {thought_id} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"Error deleting thought: {str(e)}")
            return False
    
    def delete_procedure(self, procedure_id: int) -> bool:
        """
        Delete a procedure and all its steps from the database.
        
        Args:
            procedure_id: The ID of the procedure to delete
            
        Returns:
            True if the procedure was deleted, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete the procedure (steps will be deleted automatically due to CASCADE)
            cursor.execute(
                """
                DELETE FROM procedures
                WHERE id = %s
                RETURNING id
                """,
                (procedure_id,)
            )
            
            deleted = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if deleted:
                logger.info(f"Procedure with ID {procedure_id} and all its steps deleted successfully")
                return True
            else:
                logger.warning(f"Procedure with ID {procedure_id} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"Error deleting procedure: {str(e)}")
            return False
    
    def update_thought(self, thought_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a thought in the database.
        
        Args:
            thought_id: The ID of the thought to update
            data: Dictionary containing the fields to update
            
        Returns:
            The updated thought data, or None if not found or error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if thought exists
            cursor.execute(
                "SELECT id FROM thoughts WHERE id = %s",
                (thought_id,)
            )
            
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                logger.warning(f"Thought with ID {thought_id} not found for update")
                return None
            
            # Build the update query dynamically based on provided fields
            update_fields = []
            update_values = []
            
            if 'transcription' in data and data['transcription'] is not None:
                update_fields.append("transcription = %s")
                update_values.append(data['transcription'])
                
            if 'processed' in data and data['processed'] is not None:
                update_fields.append("processed = %s")
                update_values.append(data['processed'])
                
            if 'categories' in data and data['categories'] is not None:
                update_fields.append("categories = %s")
                update_values.append(data['categories'])
                
            if 'tags' in data and data['tags'] is not None:
                update_fields.append("tags = %s")
                update_values.append(data['tags'])
                
            if 'type' in data and data['type'] is not None:
                update_fields.append("type = %s")
                update_values.append(data['type'])
                
            if 'priority' in data and data['priority'] is not None:
                update_fields.append("priority = %s")
                update_values.append(data['priority'])
                
            if 'summary' in data and data['summary'] is not None:
                update_fields.append("summary = %s")
                update_values.append(data['summary'])
            
            if not update_fields:
                cursor.close()
                conn.close()
                logger.warning("No fields to update for thought")
                return self.get_thought(thought_id)  # Return current state if no updates
            
            # Construct and execute the update query
            update_query = f"""
                UPDATE thoughts
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id
            """
            
            update_values.append(thought_id)  # Add the ID for the WHERE clause
            
            cursor.execute(update_query, update_values)
            updated = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if updated:
                logger.info(f"Thought with ID {thought_id} updated successfully")
                return self.get_thought(thought_id)  # Get the updated thought
            else:
                logger.warning(f"Failed to update thought with ID {thought_id}")
                return None
        except Exception as e:
            logger.error(f"Error updating thought: {str(e)}")
            return None
    
    def update_procedure(self, procedure_id: int, title: str, description: Optional[str] = None, trigger_phrases: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Update a procedure in the database.
        
        Args:
            procedure_id: The ID of the procedure to update
            title: The new title of the procedure
            description: Optional new description of the procedure
            trigger_phrases: Optional new list of trigger phrases
            
        Returns:
            The updated procedure data, or None if not found or error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if procedure exists
            cursor.execute(
                "SELECT id FROM procedures WHERE id = %s",
                (procedure_id,)
            )
            
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                logger.warning(f"Procedure with ID {procedure_id} not found for update")
                return None
            
            # Update the procedure
            cursor.execute(
                """
                UPDATE procedures
                SET title = %s, description = %s, trigger_phrases = %s
                WHERE id = %s
                RETURNING id
                """,
                (title, description, trigger_phrases or [], procedure_id)
            )
            
            updated = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if updated:
                logger.info(f"Procedure with ID {procedure_id} updated successfully")
                return self.get_procedure(procedure_id)  # Get the updated procedure
            else:
                logger.warning(f"Failed to update procedure with ID {procedure_id}")
                return None
        except Exception as e:
            logger.error(f"Error updating procedure: {str(e)}")
            return None
    
    def update_procedure_step(self, step_id: int, content: str, order: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Update a procedure step in the database.
        
        Args:
            step_id: The ID of the step to update
            content: The new content of the step
            order: Optional new order of the step
            
        Returns:
            The updated step data, or None if not found or error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if step exists and get its procedure_id
            cursor.execute(
                """SELECT procedure_id, "order" FROM procedure_steps WHERE id = %s""",
                (step_id,)
            )
            
            step_data = cursor.fetchone()
            if not step_data:
                cursor.close()
                conn.close()
                logger.warning(f"Step with ID {step_id} not found for update")
                return None
            
            procedure_id, current_order = step_data
            
            # If order is not provided, keep the current order
            if order is None:
                order = current_order
            
            # Update the step
            cursor.execute(
                """
                UPDATE procedure_steps
                SET content = %s, "order" = %s
                WHERE id = %s
                RETURNING id, procedure_id, content, "order", created_at
                """,
                (content, order, step_id)
            )
            
            updated_step = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if updated_step:
                logger.info(f"Step with ID {step_id} updated successfully")
                return {
                    'id': updated_step[0],
                    'procedure_id': updated_step[1],
                    'content': updated_step[2],
                    'order': updated_step[3],
                    'created_at': updated_step[4]
                }
            else:
                logger.warning(f"Failed to update step with ID {step_id}")
                return None
        except Exception as e:
            logger.error(f"Error updating procedure step: {str(e)}")
            return None
            
    # Technical Decisions methods
    def create_technical_decision(self, title: str, context: str, decision: str, reasoning: str, 
                                alternatives: List[Dict[str, Any]] = None, consequences: List[str] = None,
                                tags: List[str] = None, related_resources: List[str] = None) -> Optional[int]:
        """
        Create a new technical decision in the database.
        
        Args:
            title: The title of the technical decision
            context: The context in which the decision was made
            decision: The decision that was made
            reasoning: The reasoning behind the decision
            alternatives: Optional list of alternative options that were considered
            consequences: Optional list of consequences of the decision
            tags: Optional list of tags for the decision
            related_resources: Optional list of related resources
            
        Returns:
            The ID of the created technical decision, or None if there was an error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert the technical decision
            cursor.execute(
                """
                INSERT INTO technical_decisions (
                    title, context, decision, reasoning, alternatives, consequences, 
                    tags, related_resources, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    title, context, decision, reasoning, 
                    json.dumps(alternatives or []), consequences or [],
                    tags or [], related_resources or [], datetime.now()
                )
            )
            
            decision_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Technical decision created with ID: {decision_id}")
            return decision_id
        except Exception as e:
            logger.error(f"Error creating technical decision: {str(e)}")
            return None
            
    def get_technical_decisions(self, limit: int = 10, offset: int = 0, tags: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get multiple technical decisions from the database.
        
        Args:
            limit: Maximum number of decisions to return
            offset: Number of decisions to skip
            tags: Optional list of tags to filter by
            
        Returns:
            A list of dictionaries containing technical decision data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id, title, context, decision, reasoning, alternatives, consequences, 
                    tags, related_resources, created_at, updated_at
                FROM technical_decisions
            """
            
            params = []
            
            # Add tag filtering if provided
            if tags and len(tags) > 0:
                query += " WHERE tags @> %s"
                params.append(tags)
            
            # Add ordering and pagination
            query += """
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            decisions = []
            for row in rows:
                decisions.append({
                    'id': row[0],
                    'title': row[1],
                    'context': row[2],
                    'decision': row[3],
                    'reasoning': row[4],
                    'alternatives': row[5],
                    'consequences': row[6],
                    'tags': row[7],
                    'related_resources': row[8],
                    'created_at': row[9],
                    'updated_at': row[10]
                })
            
            return decisions
        except Exception as e:
            logger.error(f"Error getting technical decisions from database: {str(e)}")
            return []
            
    def get_technical_decision(self, decision_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a technical decision by ID.
        
        Args:
            decision_id: The ID of the technical decision to get
            
        Returns:
            A dictionary containing the technical decision data, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 
                    id, title, context, decision, reasoning, alternatives, consequences, 
                    tags, related_resources, created_at, updated_at
                FROM technical_decisions
                WHERE id = %s
                """,
                (decision_id,)
            )
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not row:
                return None
            
            return {
                'id': row[0],
                'title': row[1],
                'context': row[2],
                'decision': row[3],
                'reasoning': row[4],
                'alternatives': row[5],
                'consequences': row[6],
                'tags': row[7],
                'related_resources': row[8],
                'created_at': row[9],
                'updated_at': row[10]
            }
        except Exception as e:
            logger.error(f"Error getting technical decision from database: {str(e)}")
            return None
            
    def update_technical_decision(self, decision_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a technical decision in the database.
        
        Args:
            decision_id: The ID of the technical decision to update
            data: Dictionary containing the fields to update
            
        Returns:
            The updated technical decision data, or None if not found or error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if technical decision exists
            cursor.execute(
                "SELECT id FROM technical_decisions WHERE id = %s",
                (decision_id,)
            )
            
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                logger.warning(f"Technical decision with ID {decision_id} not found for update")
                return None
            
            # Build the update query dynamically based on provided fields
            update_fields = []
            update_values = []
            
            field_mapping = {
                'title': 'title = %s',
                'context': 'context = %s',
                'decision': 'decision = %s',
                'reasoning': 'reasoning = %s',
                'alternatives': 'alternatives = %s',
                'consequences': 'consequences = %s',
                'tags': 'tags = %s',
                'related_resources': 'related_resources = %s'
            }
            
            for field, sql_field in field_mapping.items():
                if field in data and data[field] is not None:
                    update_fields.append(sql_field)
                    # Handle JSONB field specially
                    if field == 'alternatives':
                        update_values.append(json.dumps(data[field]))
                    else:
                        update_values.append(data[field])
            
            # Always update the updated_at timestamp
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now())
            
            if not update_fields:
                cursor.close()
                conn.close()
                logger.warning("No fields to update for technical decision")
                return self.get_technical_decision(decision_id)  # Return current state if no updates
            
            # Construct and execute the update query
            update_query = f"""
                UPDATE technical_decisions
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id
            """
            
            update_values.append(decision_id)  # Add the ID for the WHERE clause
            
            cursor.execute(update_query, update_values)
            updated = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if updated:
                logger.info(f"Technical decision with ID {decision_id} updated successfully")
                return self.get_technical_decision(decision_id)  # Get the updated technical decision
            else:
                logger.warning(f"Failed to update technical decision with ID {decision_id}")
                return None
        except Exception as e:
            logger.error(f"Error updating technical decision: {str(e)}")
            return None
            
    def delete_technical_decision(self, decision_id: int) -> bool:
        """
        Delete a technical decision from the database.
        
        Args:
            decision_id: The ID of the technical decision to delete
            
        Returns:
            True if the technical decision was deleted, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete the technical decision
            cursor.execute(
                """
                DELETE FROM technical_decisions
                WHERE id = %s
                RETURNING id
                """,
                (decision_id,)
            )
            
            deleted = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if deleted:
                logger.info(f"Technical decision with ID {decision_id} deleted successfully")
                return True
            else:
                logger.warning(f"Technical decision with ID {decision_id} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"Error deleting technical decision: {str(e)}")
            return False
            
    # Experiences methods
    def create_experience(self, title: str, situation: str, actions: List[str], outcome: str, 
                        learnings: List[str] = None, context: str = None, tags: List[str] = None, 
                        related_resources: List[str] = None, importance: str = None) -> Optional[int]:
        """
        Create a new experience in the database.
        
        Args:
            title: The title of the experience
            situation: The situation or problem faced
            actions: The actions taken
            outcome: The outcome of the actions
            learnings: Optional list of learnings from the experience
            context: Optional additional context
            tags: Optional list of tags for the experience
            related_resources: Optional list of related resources
            importance: Optional importance level (low, medium, high)
            
        Returns:
            The ID of the created experience, or None if there was an error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Insert the experience
            cursor.execute(
                """
                INSERT INTO experiences (
                    title, situation, actions, outcome, learnings, context, 
                    tags, related_resources, importance, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    title, situation, actions, outcome, learnings or [], context,
                    tags or [], related_resources or [], importance, datetime.now()
                )
            )
            
            experience_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Experience created with ID: {experience_id}")
            return experience_id
        except Exception as e:
            logger.error(f"Error creating experience: {str(e)}")
            return None
            
    def get_experiences(self, limit: int = 10, offset: int = 0, tags: List[str] = None, importance: str = None) -> List[Dict[str, Any]]:
        """
        Get multiple experiences from the database.
        
        Args:
            limit: Maximum number of experiences to return
            offset: Number of experiences to skip
            tags: Optional list of tags to filter by
            importance: Optional importance level to filter by
            
        Returns:
            A list of dictionaries containing experience data
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT 
                    id, title, situation, actions, outcome, learnings, context, 
                    tags, related_resources, importance, created_at, updated_at
                FROM experiences
            """
            
            conditions = []
            params = []
            
            # Add tag filtering if provided
            if tags and len(tags) > 0:
                conditions.append("tags @> %s")
                params.append(tags)
            
            # Add importance filtering if provided
            if importance:
                conditions.append("importance = %s")
                params.append(importance)
            
            # Add WHERE clause if we have conditions
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # Add ordering and pagination
            query += """
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            
            rows = cursor.fetchall()
            cursor.close()
            conn.close()
            
            experiences = []
            for row in rows:
                experiences.append({
                    'id': row[0],
                    'title': row[1],
                    'situation': row[2],
                    'actions': row[3],
                    'outcome': row[4],
                    'learnings': row[5],
                    'context': row[6],
                    'tags': row[7],
                    'related_resources': row[8],
                    'importance': row[9],
                    'created_at': row[10],
                    'updated_at': row[11]
                })
            
            return experiences
        except Exception as e:
            logger.error(f"Error getting experiences from database: {str(e)}")
            return []
            
    def get_experience(self, experience_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an experience by ID.
        
        Args:
            experience_id: The ID of the experience to get
            
        Returns:
            A dictionary containing the experience data, or None if not found
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                SELECT 
                    id, title, situation, actions, outcome, learnings, context, 
                    tags, related_resources, importance, created_at, updated_at
                FROM experiences
                WHERE id = %s
                """,
                (experience_id,)
            )
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not row:
                return None
            
            return {
                'id': row[0],
                'title': row[1],
                'situation': row[2],
                'actions': row[3],
                'outcome': row[4],
                'learnings': row[5],
                'context': row[6],
                'tags': row[7],
                'related_resources': row[8],
                'importance': row[9],
                'created_at': row[10],
                'updated_at': row[11]
            }
        except Exception as e:
            logger.error(f"Error getting experience from database: {str(e)}")
            return None
            
    def update_experience(self, experience_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an experience in the database.
        
        Args:
            experience_id: The ID of the experience to update
            data: Dictionary containing the fields to update
            
        Returns:
            The updated experience data, or None if not found or error
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if experience exists
            cursor.execute(
                "SELECT id FROM experiences WHERE id = %s",
                (experience_id,)
            )
            
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                logger.warning(f"Experience with ID {experience_id} not found for update")
                return None
            
            # Build the update query dynamically based on provided fields
            update_fields = []
            update_values = []
            
            field_mapping = {
                'title': 'title = %s',
                'situation': 'situation = %s',
                'actions': 'actions = %s',
                'outcome': 'outcome = %s',
                'learnings': 'learnings = %s',
                'context': 'context = %s',
                'tags': 'tags = %s',
                'related_resources': 'related_resources = %s',
                'importance': 'importance = %s'
            }
            
            for field, sql_field in field_mapping.items():
                if field in data and data[field] is not None:
                    update_fields.append(sql_field)
                    update_values.append(data[field])
            
            # Always update the updated_at timestamp
            update_fields.append("updated_at = %s")
            update_values.append(datetime.now())
            
            if not update_fields:
                cursor.close()
                conn.close()
                logger.warning("No fields to update for experience")
                return self.get_experience(experience_id)  # Return current state if no updates
            
            # Construct and execute the update query
            update_query = f"""
                UPDATE experiences
                SET {', '.join(update_fields)}
                WHERE id = %s
                RETURNING id
            """
            
            update_values.append(experience_id)  # Add the ID for the WHERE clause
            
            cursor.execute(update_query, update_values)
            updated = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if updated:
                logger.info(f"Experience with ID {experience_id} updated successfully")
                return self.get_experience(experience_id)  # Get the updated experience
            else:
                logger.warning(f"Failed to update experience with ID {experience_id}")
                return None
        except Exception as e:
            logger.error(f"Error updating experience: {str(e)}")
            return None
            
    def delete_experience(self, experience_id: int) -> bool:
        """
        Delete an experience from the database.
        
        Args:
            experience_id: The ID of the experience to delete
            
        Returns:
            True if the experience was deleted, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Delete the experience
            cursor.execute(
                """
                DELETE FROM experiences
                WHERE id = %s
                RETURNING id
                """,
                (experience_id,)
            )
            
            deleted = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            if deleted:
                logger.info(f"Experience with ID {experience_id} deleted successfully")
                return True
            else:
                logger.warning(f"Experience with ID {experience_id} not found for deletion")
                return False
        except Exception as e:
            logger.error(f"Error deleting experience: {str(e)}")
            return False
