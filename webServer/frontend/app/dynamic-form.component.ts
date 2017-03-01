import { Params }   from '@angular/router';
import { Component, EventEmitter, Input, OnInit, Output }  from '@angular/core';
import { FormGroup }                 from '@angular/forms';
import { QuestionBase }              from './question-base';
import { QuestionControlService }    from './question-control.service';

import 'rxjs/add/operator/switchMap';

@Component({
  moduleId: module.id,
  selector: 'dynamic-form',
  templateUrl: 'dynamic-form.component.html',
  providers: [ QuestionControlService ]
})

export class DynamicFormComponent implements OnInit {
  @Input() questions: QuestionBase<any>[] = [];
  @Output() formJson: EventEmitter<string> = new EventEmitter<string>();

  form: FormGroup;
  errMsg = '';
  id:number;
  componentName:string;
  
  constructor(
    private qcs: QuestionControlService, 
  ) {}

  ngOnInit() {
    this.form = this.qcs.toFormGroup(this.questions);
    this.form.valueChanges.subscribe(data => this.formChanged(data))
  }

  formChanged(data: string) {
    this.formJson.emit(data);
  }
 
}

