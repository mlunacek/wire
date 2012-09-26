from django.db import models

class Nodes(models.Model):
    node = models.CharField(max_length=8,primary_key=True)
    def __unicode__(self):
        return str(self.node)

class Summary(models.Model):
    node = models.CharField(max_length=8,primary_key=True)
    stream =  models.BooleanField()
    linpack =  models.BooleanField()
    bandwidth =  models.BooleanField()

class BaseTest(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=8)
    test_date = models.DateTimeField(db_index=True)
    test1 = models.FloatField()
    test2 = models.FloatField()
    test3 = models.FloatField()
    test4 = models.FloatField()
    effective = models.BooleanField()
    p_index = models.FloatField(null=True)
    p_test1 = models.FloatField(null=True)
    p_test2 = models.FloatField(null=True)
    p_test3 = models.FloatField(null=True)
    p_test4 = models.FloatField(null=True)
    
    class Meta:
        abstract = True
        
    def __unicode__(self):
        return str(self.id)
    
    def calculat_pdiff(self, m1, m2, m3, m4):
        self.p_test1 = round((m1 - self.test1)/m1*100)
        self.p_test2 = round((m2 - self.test2)/m2*100)
        self.p_test3 = round((m3 - self.test3)/m3*100)
        self.p_test4 = round((m4 - self.test4)/m4*100)
        self.p_index = max(self.p_test1, self.p_test2, self.p_test3, self.p_test4)
    
             
class Stream(BaseTest):
    node = models.CharField(max_length=8)
    
    class Meta:
        unique_together = ('test_date', 'node')
    
class Linpack(BaseTest):        
    node = models.CharField(max_length=8)
    
    class Meta:
        unique_together = ('test_date', 'node')
    
class Bandwidth(BaseTest):
            
    node1 = models.CharField(max_length=8)      
    node2 = models.CharField(max_length=8)   
    
    class Meta:
        unique_together = ('test_date', 'node1', 'node2')  