import { Component, Input, OnInit, ViewChild } from '@angular/core';
import { BaseChartDirective } from 'ng2-charts/ng2-charts';
import { ActivatedRoute, Params }   from '@angular/router';
import { Location }                 from '@angular/common';

import { DropdownQuestion } from './question-dropdown';
import { ObjectData } from './object-data';
import { QuestionBase }     from './question-base';
import { QuestionService } from './question.service';
import { TextboxQuestion }  from './question-textbox';
import { TransitionService } from './transition.service';
import { Transition }         from './transition';
import 'rxjs/add/operator/switchMap';



@Component({
  moduleId: module.id,
  selector: 'my-transition-detail',
  templateUrl: 'transition-detail.component.html',
  styleUrls: [ 'transition-detail.component.css' ] 
})


export class TransitionDetailComponent implements OnInit {
  @ViewChild(BaseChartDirective) chart: BaseChartDirective;
  transition: Transition;
  objectData: ObjectData;
  dataSets: Array<any> = [{'data':[0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'label':'close'}];
  labels: Array<any> = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13'];

  results: Array<any> = [{'data':[0,0,0,0,0,0,0,0,0,0,0,0,0,0], 'label':'ROI'}];
  transitionQuestions: any[] = [];
  parameterQuestions: any[] = [];
  isFormChanged: boolean;
  errMsg: any;

  constructor(
    private transitionService: TransitionService,
    private questionService: QuestionService,
    private route: ActivatedRoute,
    private location: Location
  ) {}

  ngOnInit(): void {
    this.route.params
      .switchMap((params: Params) => this.transitionService.getTransition(+params['id']))
      .subscribe(transition => this.transitionUpdated(transition));

      
  }

  goBack(): void {
    this.location.back();
  }
  
  onChange(formValue: string):void{
    let updatedFieldJson = JSON.stringify(formValue);
    this.transition.updateFromJson(updatedFieldJson);
    this.isFormChanged = true;
  }

  onParameterChange(formValue: string): void{
    let parametersJson = JSON.stringify(formValue);
    this.transition.setParameters(parametersJson);
    this.isFormChanged = true;
  }

  onUpdate():void {
    this.transitionService.updateTransition(JSON.stringify(this.transition), this.transition.id).
          then(transition => this.transitionUpdated(transition),
               error =>  this.errMsg = <any>error);
    this.isFormChanged = false;
  }

  transitionUpdated(transition:Transition): void {
    this.transition = new Transition();
    this.transition.updateFromObject(transition); 
    this.transitionQuestions = this.questionService.getQuestionsFromTrans(transition); 
    this.parameterQuestions = this.questionService.getQuestionsFromParameters(transition.customizeParameter); 
    this.transitionService.getTransitionObjectData(this.transition.id).then(objectData => this.updateObjectData(objectData),
                 error => this.errMsg = <any>error);
  }

  onRunTransition(): void{
    if(this.isFormChanged)
    {
      this.onUpdate();
    }
    this.transitionService.getTransitionResults(this.transition.id)
           .then(objectData => this.updateObjectData(objectData),
                 error => this.errMsg = <any>error);
  }

  updateObjectData(objectData: ObjectData): void{
    this.objectData = objectData; 
    this.dataSets = objectData.dataSets; 
    this.labels = objectData.labels; 
    this.results = objectData.results;
    //ng2-charts@1.5.0 has bug for update labels,
    //remove following work around in later version
    setTimeout(() => {
            if (this.chart && this.chart.chart && this.chart.chart.config) {
                this.chart.chart.config.data.labels = this.labels;
                this.chart.chart.update();
            }
        });
  }
}

