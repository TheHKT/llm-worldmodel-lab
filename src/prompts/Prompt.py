from abc import ABC, abstractmethod
import json
import uuid

class Prompt(ABC):    
    def __init__(self, playbook='', reflection='', generatorOutput='', playbook_path="res/playbook.json"):
        self.playbook_path = playbook_path
        self.playbook = self.readPlaybookFromFile() # Created by curator
        self.reflection = reflection # Created by reflector
        self.generatorOutput = generatorOutput # Created by generator
        
    
    @abstractmethod
    def getGeneratorPrompt(self, state='') -> str:
        pass
    
    @abstractmethod
    def getReflectorPrompt(self) -> str:
        pass
    
    @abstractmethod
    def getCuratorPrompt(self) -> str:
        pass
    
    @abstractmethod
    def getGeneratorTools(self) -> str:
        pass
    
    @abstractmethod
    def getCuratorTools(self) -> str:
        pass
        
    def refreshPlaybook(self):
        self.playbook = self.readPlaybookFromFile()
        
    def setReflection(self, reflection: str):
        self.reflection = reflection
        reflection_obj = json.loads(reflection) 
        
        bullet_tags = reflection_obj.get("bullet_tags", [])
        
        for tag in bullet_tags:
            bullet_id = tag.get("id")
            tag_type = tag.get("tag")
            
            for sec in self.playbook.get("sections", []):
                for bp in sec.get("bulletpoints", []):
                    if bullet_id == bp["id"]:
                        bp[tag_type] += 1
                        break
        self.writePlaybookToFile()
        
    def setGeneratorOutput(self, generatorOutput: str):
        self.generatorOutput = generatorOutput
        
    def getPlaybookAsString(self) -> str:
        out = []
        for i, sec in enumerate(self.playbook.get("sections", []), 1):
            title = sec.get("title", "").strip() or f"Section {i}"
            out.append(f"{i}. {title}")
            for bp in sec.get("bulletpoints", []):
                bid = bp.get("id", "")
                content = bp.get("content", "")
                helpful = bp.get("helpful", 0)
                harmful = bp.get("harmful", 0)
                out.append(f"   - [{bid}] {content.strip()}; helpful: {helpful}, harmful: {harmful}")
        return "\n".join(out)   
    
    def _find_section(self, title):
        if title is None:
            return None
        for sec in self.playbook["sections"]:
            if sec.get("title") == title:
                return sec
        return None
    
    def addFromPlaybook(self, section, content):
      sec = self._find_section(section)
      if sec is None:
          sec = {"title": section, "bulletpoints": []}
          self.playbook["sections"].append(sec)
      bullet_id = str(uuid.uuid4())
      sec["bulletpoints"].append({"id": bullet_id, "content": content, "helpful": 0, "harmful": 0})  
      self.writePlaybookToFile()
    
    def removeFromPlaybook(self, bullet_id):
        for sec in self.playbook["sections"]:
            new_bullets = []
            removed = False
            for bp in sec["bulletpoints"]:
                if bullet_id == bp["id"]:
                    removed = True
                    continue
                new_bullets.append(bp)
            if removed:
                sec["bulletpoints"] = new_bullets
        self.writePlaybookToFile()    
    
    def modifyFromPlaybook(self, bullet_id, content):
        for sec in self.playbook["sections"]:
            for bp in sec["bulletpoints"]:
                if bullet_id == bp["id"]:
                    bp["content"] = content
        self.writePlaybookToFile()
    
    def readPlaybookFromFile(self):
        try:
            with open(self.playbook_path, 'r', encoding='utf-8') as file:
                content = file.read()
                if not content.strip():
                    return {"sections": [{}]}
                return json.loads(content)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"sections": []}
        
    def writePlaybookToFile(self):
        with open(self.playbook_path, 'w', encoding='utf-8') as file:
            json.dump(self.playbook, file, indent=4)    
            