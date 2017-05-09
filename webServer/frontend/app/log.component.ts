import { LogService, LogMessage } from './log.service';
import { Component, ElementRef, Input, OnInit, OnDestroy } from '@angular/core';
import { Subject } from 'rxjs/Rx';

@Component({
  selector: 'log',
  template: `
            <div (window:beforeunload)="onCloseWindows()"></div> 
            <div class="messages">
            <p *ngFor="let msg of logMessages">{{ msg.message }}</p>
            </div>
            <button (click)="connect()" [hidden]="transitionName!='Debug'">Connect</button>
	    <button (click)="disconnect()" [hidden]="transitionName!='Debug'">Disconnect</button>
	    `
})
export class LogComponent implements OnInit, OnDestroy {
  @Input() transitionName: string = 'Debug';
  private logMessages: LogMessage[] = new Array();
  private ctrlMessage = {
      name: this.transitionName,
      message: '',
  }

  constructor(private logService: LogService) {
    logService.logMessages.subscribe(msg => {
      this.logMessages.push(msg);
    });
  }

  ngOnInit() {
  }

  ngOnDestroy() {
    this.disconnect();
  }

  connect() {
    this.ctrlMessage.name = this.transitionName;
    this.ctrlMessage.message = 'connect';
    this.logService.logMessages.next(this.ctrlMessage);
  } 
  
  disconnect() {
    this.ctrlMessage.name = this.transitionName;
    this.ctrlMessage.message = 'disconnect';
    this.logService.logMessages.next(this.ctrlMessage);
  }

  onCloseWindows() {
    this.disconnect();
  }
}
